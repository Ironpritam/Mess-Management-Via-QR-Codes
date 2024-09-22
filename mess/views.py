from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from mess.models import Student
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from .qr import encode, decode
from django.conf import settings
# from PIL import Image
from datetime import datetime, time


# Create your views here.

def vendorscan(request):
    if request.method == 'POST':
        qr_image = request.FILES.get('qr_image')
        student_name = decode(qr_image) 
        
        if student_name:
            current_time = datetime.now()
            meal_type, meal_flag = classify_meal_type(current_time)
            
            if meal_type and meal_flag:
                try:
                    # Get the student from the database
                    student = Student.objects.get(name=student_name)
                    
                    # Check if the student has eaten the classified meal for the current date
                    has_eaten = check_meal_consumption(meal_type, student_name, current_time.day)
                    
                    if not has_eaten:
                        # Update the meal_data only if the student has not eaten the classified meal for the current date
                        meal_data = student.meal_data
                        date_index = current_time.day - 1  # Index starts from 0

                        # Add the meal_flag to the date index in meal_data
                        meal_data = list(meal_data)
                        meal_data[date_index] = str(int(meal_data[date_index]) | meal_flag)
                        student.meal_data = ''.join(meal_data)
                        student.save()
                        return render(request, 'vendorscan.html', {'message': f"{student_name}'s {meal_type.lower()} successfully checked."})

                    # Render the same page with the result message
                    return render(request, 'vendorscan.html', {'message': f"{student_name} has already eaten {meal_type.lower()} today."})
                except Student.DoesNotExist:
                    return HttpResponse("Student not found")

    # Render the initial form page for QR scanning
    return render(request, 'vendorscan.html', {'message': ''})


def signup_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        # edit qr code and save
        qr_code=name
        password = request.POST.get('password')
        # guard for student existing
        try:
            student = Student.objects.get(name=student_name)
            return HttpResponse("Student already exists")
        except:
            pass
        student = Student(name=name, qr_code=qr_code, password=password, meal_data="0000000000000000000000000000000")
        # You might perform additional checks here before saving the student
        student.save()
        imagedata = encode(qr_code)
        qr_code_image = imagedata.png(f'{settings.QR_CODE_DIR}/{name}.png', scale=6)

        # return HttpResponse("Student created successfully!") # send to profile
        return render(request, 'profile.html', {'user_name': name, 'image_path': f'{name}.png', 'meal_data': student.meal_data})
    return render(request, 'signup.html')

def login_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        password = request.POST.get('password')

        try:
            student = Student.objects.get(name=name, password=password)
            # Perform additional verification if needed
            # return HttpResponse("Login successful!") # send to profile
            return render(request, 'profile.html', {'user_name': name, 'image_path': f'{name}.png', 'meal_data': student.meal_data})

        except Student.DoesNotExist:
            return HttpResponse("Invalid credentials. Please try again.")

    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect("home")

def QRlogin_view(request):
    if request.method == 'POST':
        qr_image = request.FILES.get('qr_image')

        if qr_image:
            # print(qr_image)
            qr_text = decode(qr_image)
            # print(qr_text)
            if qr_text:
                try:
                    student = Student.objects.get(qr_code=qr_text)
                    # return HttpResponse(f"Login successful! Welcome, {student.name}!") # send to profile
                    return render(request, 'profile.html', {'user_name': student.name, 'image_path': f'{student.name}.png', 'meal_data': student.meal_data})
                except Student.DoesNotExist:
                    return HttpResponse("User not found. Please try again.")
            else:
                return HttpResponse("Invalid QR code. Please try again.")
        else:
            return HttpResponse("No QR code submitted. Please select an image.")

    return render(request, 'loginqr.html')


def home(request):
    template = loader.get_template('home.html')
    return HttpResponse(template.render())
#########################################################################
#                        HELPER FUNCTIONS                               #
#########################################################################
def check_meal_consumption(meal_type, student_name, date):
    meal_types = {'BREAKFAST': 1, 'LUNCH': 2, 'DINNER': 4} 
    meal_flag = meal_types.get(meal_type.upper())  
    try:
        student = Student.objects.get(name=student_name)
    except Student.DoesNotExist:
        return False
    # Get the student's meal_data string and check if the meal was consumed on the given date
    meal_data = student.meal_data
    meal_at_date = int(meal_data[date-1])
    if (meal_at_date & meal_flag) > 0: # bitwise AND with the flag
        return True
    else:
        return False

def classify_meal_type(current_time):
    # Define time ranges for meals
    breakfast_start = time(7, 0)  # 7:00 AM
    breakfast_end = time(11, 0)   # 11:00 AM
    lunch_start = time(12, 0)     # 12:00 PM
    lunch_end = time(15, 0)       # 3:00 PM
    dinner_start = time(19, 0)    # 7:00 PM
    dinner_end = time(23, 0)      # 11:00 PM

    current_hour = current_time.time()

    if breakfast_start <= current_hour <= breakfast_end:
        return 'BREAKFAST', 1
    elif lunch_start <= current_hour <= lunch_end:
        return 'LUNCH', 2
    elif dinner_start <= current_hour <= dinner_end:
        return 'DINNER', 4
    else:
        return None, None
