import os
from datetime import datetime, time
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.conf import settings

from mess.models import Student, MealTransaction
from mess.qr import encode, decode
from analytics_engine.meal_forecaster import MealForecaster


def vendorscan(request):
    if request.method == 'POST':
        qr_image = request.FILES.get('qr_image')
        if not qr_image:
            return render(request, 'vendorscan.html', {'message': 'Please upload or capture a QR code image.'})

        student_name = decode(qr_image)

        if student_name:
            current_time = datetime.now()
            meal_type, meal_flag = classify_meal_type(current_time)

            if not meal_type or not meal_flag:
                return render(request, 'vendorscan.html', {
                    'message': f"Scan rejected: Outside defined mess operating hours (Current time: {current_time.strftime('%H:%M')})."
                })

            try:
                student = Student.objects.get(name=student_name)
                has_eaten = check_meal_consumption(meal_type, student_name, current_time.day)

                if not has_eaten:
                    # Update meal data bitmask
                    student.record_meal(current_time.day, meal_flag)

                    # Log audit transaction
                    MealTransaction.objects.create(
                        student=student,
                        meal_type=meal_type,
                        status='SUCCESS'
                    )

                    return render(request, 'vendorscan.html', {
                        'message': f"SUCCESS: {student.name}'s {meal_type.lower()} recorded.",
                        'status_type': 'success',
                        'student': student,
                        'meal_type': meal_type
                    })

                # Log duplicate scan attempt
                MealTransaction.objects.create(
                    student=student,
                    meal_type=meal_type,
                    status='ALREADY_SERVED'
                )

                return render(request, 'vendorscan.html', {
                    'message': f"WARNING: {student.name} has already eaten {meal_type.lower()} today.",
                    'status_type': 'warning',
                    'student': student,
                    'meal_type': meal_type
                })

            except Student.DoesNotExist:
                return render(request, 'vendorscan.html', {
                    'message': f"ERROR: Student identifier '{student_name}' not registered in system.",
                    'status_type': 'danger'
                })
        else:
            return render(request, 'vendorscan.html', {
                'message': 'ERROR: QR code could not be detected/decoded. Please try a clearer scan.',
                'status_type': 'danger'
            })

    return render(request, 'vendorscan.html', {'message': ''})


def signup_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        password = request.POST.get('password')
        qr_code = name

        if Student.objects.filter(name=name).exists():
            return render(request, 'signup.html', {'error': 'Student with this name already exists.'})

        student = Student.objects.create(
            name=name,
            qr_code=qr_code,
            password=password,
            meal_data="0" * 31
        )

        # Generate & save QR code image
        os.makedirs(settings.QR_CODE_DIR, exist_ok=True)
        qr_path = os.path.join(settings.QR_CODE_DIR, f"{name}.png")
        encode(qr_code).png(qr_path, scale=6)

        return render(request, 'profile.html', {
            'user_name': name,
            'image_path': f"{name}.png",
            'meal_data': student.meal_data
        })

    return render(request, 'signup.html')


def login_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        password = request.POST.get('password')

        try:
            student = Student.objects.get(name=name, password=password)
            return render(request, 'profile.html', {
                'user_name': student.name,
                'image_path': f"{student.name}.png",
                'meal_data': student.meal_data
            })
        except Student.DoesNotExist:
            return render(request, 'login.html', {'error': 'Invalid credentials. Please try again.'})

    return render(request, 'login.html')


def logout_view(request):
    return redirect("home")


def QRlogin_view(request):
    if request.method == 'POST':
        qr_image = request.FILES.get('qr_image')
        if qr_image:
            qr_text = decode(qr_image)
            if qr_text:
                try:
                    student = Student.objects.get(qr_code=qr_text)
                    return render(request, 'profile.html', {
                        'user_name': student.name,
                        'image_path': f"{student.name}.png",
                        'meal_data': student.meal_data
                    })
                except Student.DoesNotExist:
                    return render(request, 'loginqr.html', {'error': f"User '{qr_text}' not found."})
            else:
                return render(request, 'loginqr.html', {'error': 'Invalid QR code. Could not decode image.'})
        else:
            return render(request, 'loginqr.html', {'error': 'No QR code submitted. Please upload an image.'})

    return render(request, 'loginqr.html')


def home(request):
    template = loader.get_template('home.html')
    return HttpResponse(template.render({}, request))


def analytics_dashboard(request):
    """
    AI Predictive Analytics & Mess Manager Dashboard.
    """
    students_meal_data = list(Student.objects.values_list('meal_data', flat=True))
    forecaster = MealForecaster(students_meal_data)
    forecast_data = forecaster.forecast_meal_demand()

    recent_transactions = MealTransaction.objects.select_related('student').order_by('-timestamp')[:10]

    return render(request, 'analytics.html', {
        'forecast': forecast_data,
        'recent_transactions': recent_transactions,
        'total_students': len(students_meal_data)
    })


#########################################################################
#                        HELPER FUNCTIONS                               #
#########################################################################
def check_meal_consumption(meal_type, student_name, date):
    meal_types = {'BREAKFAST': 1, 'LUNCH': 2, 'DINNER': 4}
    meal_flag = meal_types.get(meal_type.upper())
    try:
        student = Student.objects.get(name=student_name)
        return student.has_eaten_meal(date, meal_flag)
    except Student.DoesNotExist:
        return False


def classify_meal_type(current_time):
    breakfast_start, breakfast_end = time(7, 0), time(11, 0)
    lunch_start, lunch_end = time(12, 0), time(15, 0)
    dinner_start, dinner_end = time(19, 0), time(23, 0)

    current_hour = current_time.time()

    if breakfast_start <= current_hour <= breakfast_end:
        return 'BREAKFAST', 1
    elif lunch_start <= current_hour <= lunch_end:
        return 'LUNCH', 2
    elif dinner_start <= current_hour <= dinner_end:
        return 'DINNER', 4
    else:
        # Fallback for testing/demonstration outside standard meal hours
        return 'LUNCH', 2
