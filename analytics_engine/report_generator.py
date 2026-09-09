import csv
import os
from datetime import datetime
from typing import List, Dict, Any


def export_meal_data_to_csv(students_data: List[Any], csv_file_path: str = "reports/student_meal_export.csv") -> str:
    """
    Exports student meal consumption bitwise logs to CSV format and returns absolute path.
    """
    output_dir = os.path.dirname(csv_file_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        
        # Header
        writer.writerow(['Student Name', 'QR Code Data', 'Days Active (of 31)', 'Bitwise Meal Log', 'Total Meals Consumed'])
        
        for student in students_data:
            meal_str = getattr(student, 'meal_data', '0'*31)
            name = getattr(student, 'name', 'Unknown')
            qr_code = getattr(student, 'qr_code', 'N/A')
            
            # Calculate total meals consumed from bitwise mask
            total_meals = sum(bin(int(char)).count('1') for char in meal_str if char.isdigit())
            active_days = sum(1 for char in meal_str if char != '0')
            
            writer.writerow([name, qr_code, active_days, meal_str, total_meals])
            
    return os.path.abspath(csv_file_path)


def generate_monthly_analytics_summary(students_data: List[Any]) -> Dict[str, Any]:
    """
    Computes aggregated monthly analytics summary across all students.
    """
    total_students = len(students_data)
    total_breakfasts = 0
    total_lunches = 0
    total_dinners = 0

    for s in students_data:
        meal_str = getattr(s, 'meal_data', '0'*31)
        for char in meal_str:
            if char.isdigit():
                val = int(char)
                if val & 1:
                    total_breakfasts += 1
                if val & 2:
                    total_lunches += 1
                if val & 4:
                    total_dinners += 1

    return {
        "generated_at": datetime.now().isoformat(),
        "total_enrolled_students": total_students,
        "monthly_totals": {
            "breakfasts_served": total_breakfasts,
            "lunches_served": total_lunches,
            "dinners_served": total_dinners,
            "total_meals_served": total_breakfasts + total_lunches + total_dinners
        },
        "average_meals_per_student": round((total_breakfasts + total_lunches + total_dinners) / max(1, total_students), 2)
    }
