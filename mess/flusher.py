"""
Monthly Data Flusher & Exporter Script for SmartMess AI.
Exports current month's attendance records to CSV and resets student meal data.
"""
import os
import sys
import django

# Setup Django Environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mess_manage.settings')
django.setup()

from mess.models import Student
from analytics_engine.report_generator import export_meal_data_to_csv, generate_monthly_analytics_summary


def run_monthly_flush():
    students = Student.objects.all()
    print(f"[SmartMess AI] Found {students.count()} student records.")

    # 1. Export CSV
    csv_path = export_meal_data_to_csv(list(students), csv_file_path="reports/monthly_mess_report.csv")
    print(f"[SmartMess AI] Successfully exported monthly records to: {csv_path}")

    # 2. Print Summary Analytics
    summary = generate_monthly_analytics_summary(list(students))
    print("\n--- Monthly Analytics Summary ---")
    print(f"Total Enrolled Students : {summary['total_enrolled_students']}")
    print(f"Total Breakfasts Served : {summary['monthly_totals']['breakfasts_served']}")
    print(f"Total Lunches Served    : {summary['monthly_totals']['lunches_served']}")
    print(f"Total Dinners Served    : {summary['monthly_totals']['dinners_served']}")
    print(f"Total Meals Served      : {summary['monthly_totals']['total_meals_served']}")
    print("---------------------------------\n")

    # 3. Reset Meal Data Strings
    students.update(meal_data="0" * 31)
    print("[SmartMess AI] Successfully reset all student meal_data bitmasks to zero for the new month.")


if __name__ == '__main__':
    run_monthly_flush()
