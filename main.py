"""
Unified CLI & Application Launcher for SmartMess AI.
Supports web portal, FastAPI microservice, CLI scanning, and analytics export.
"""
import argparse
import sys
import os
import django

def setup_django():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mess_manage.settings')
    django.setup()

def main():
    parser = argparse.ArgumentParser(
        description="SmartMess AI: Computer Vision & Edge QR Mess Management System"
    )
    parser.add_argument("--web", action="store_true", help="Launch Django Web Portal")
    parser.add_argument("--api", action="store_true", help="Launch FastAPI REST Microservice")
    parser.add_argument("--forecast", action="store_true", help="Run AI Meal Demand Forecaster")
    parser.add_argument("--scan", type=str, help="Run CLI QR scan on image file path")
    parser.add_argument("--export", action="store_true", help="Export monthly attendance records to CSV")
    
    args = parser.parse_args()
    
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)
        
    setup_django()
    
    if args.web:
        print("[SmartMess AI] Launching Django Web Portal on http://127.0.0.1:8000 ...")
        from django.core.management import execute_from_command_line
        execute_from_command_line(["manage.py", "runserver", "0.0.0.0:8000"])
        
    elif args.api:
        print("[SmartMess AI] Launching FastAPI Edge REST API Microservice on http://127.0.0.1:8001 ...")
        import uvicorn
        uvicorn.run("api_server:app", host="0.0.0.0", port=8001, reload=True)
        
    elif args.forecast:
        from mess.models import Student
        from analytics_engine.meal_forecaster import MealForecaster
        students_meal_data = list(Student.objects.values_list('meal_data', flat=True))
        forecaster = MealForecaster(students_meal_data)
        res = forecaster.forecast_meal_demand()
        print("\n--- SmartMess AI Predictive Demand Forecast ---")
        print(f"Target Day              : Day {res['target_day']}")
        print(f"Enrolled Students       : {res['total_enrolled_students']}")
        print(f"Forecasted Breakfast    : {res['forecasted_attendance']['breakfast']} students")
        print(f"Forecasted Lunch        : {res['forecasted_attendance']['lunch']} students")
        print(f"Forecasted Dinner       : {res['forecasted_attendance']['dinner']} students")
        print(f"Prevented Waste         : {res['waste_optimization']['estimated_food_waste_prevented_kg']} kg")
        print(f"Estimated INR Savings   : INR {res['waste_optimization']['estimated_daily_savings_inr']}")
        print("-----------------------------------------------\n")
        
    elif args.scan:
        from vision_engine.qr_detector import detect_and_decode_qr
        data, meta = detect_and_decode_qr(args.scan)
        print("\n--- SmartMess AI CLI Scanner ---")
        print(f"File Path    : {args.scan}")
        print(f"Success      : {meta.get('success')}")
        print(f"Backend Used : {meta.get('backend')}")
        print(f"Decoded Data : {data}")
        print("--------------------------------\n")
        
    elif args.export:
        from mess.flusher import run_monthly_flush
        run_monthly_flush()

if __name__ == "__main__":
    main()
