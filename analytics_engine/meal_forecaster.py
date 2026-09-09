import numpy as np
from typing import Dict, List, Any, Tuple
from datetime import datetime


class MealForecaster:
    """
    Predictive AI Analytics engine for institutional mess management.
    Parses bitwise attendance records and models meal turnout & ingredient demand.
    """

    MEAL_FLAGS = {
        "BREAKFAST": 1,
        "LUNCH": 2,
        "DINNER": 4
    }

    # Average per-student raw ingredient consumption (in grams/units)
    PER_STUDENT_PORTION = {
        "BREAKFAST": {"Milk_L": 0.2, "Bread_slices": 4, "Eggs": 2, "Poha_g": 120},
        "LUNCH": {"Rice_g": 150, "Atta_g": 100, "Dal_g": 60, "Veggies_g": 120},
        "DINNER": {"Rice_g": 120, "Atta_g": 120, "Dal_g": 60, "Paneer_g": 80}
    }

    def __init__(self, students_meal_data: List[str] = None):
        """
        Initialize with a list of 31-character meal_data strings from Student model.
        """
        self.students_meal_data = students_meal_data or []

    def parse_attendance_matrix(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Parse student meal_data strings into daily attendance counts for 31 days.
        Returns tuple of 1D arrays: (breakfast_counts, lunch_counts, dinner_counts)
        """
        num_students = len(self.students_meal_data)
        if num_students == 0:
            return np.zeros(31), np.zeros(31), np.zeros(31)

        bf_counts = np.zeros(31, dtype=int)
        lunch_counts = np.zeros(31, dtype=int)
        dinner_counts = np.zeros(31, dtype=int)

        for meal_str in self.students_meal_data:
            if not meal_str or len(meal_str) < 31:
                continue
            for day_idx in range(min(31, len(meal_str))):
                val = int(meal_str[day_idx])
                if val & self.MEAL_FLAGS["BREAKFAST"]:
                    bf_counts[day_idx] += 1
                if val & self.MEAL_FLAGS["LUNCH"]:
                    lunch_counts[day_idx] += 1
                if val & self.MEAL_FLAGS["DINNER"]:
                    dinner_counts[day_idx] += 1

        return bf_counts, lunch_counts, dinner_counts

    def forecast_meal_demand(self, target_day: int = None) -> Dict[str, Any]:
        """
        Predict attendance and ingredient requirements for a target day of the month.
        Uses exponential weighted moving average (EMA) & participation rates across past days.
        """
        if target_day is None:
            target_day = datetime.now().day

        bf_counts, lunch_counts, dinner_counts = self.parse_attendance_matrix()
        total_students = max(1, len(self.students_meal_data))

        # Active days so far (days before or up to target_day with scans)
        past_days = [d for d in range(target_day - 1) if (bf_counts[d] + lunch_counts[d] + dinner_counts[d]) > 0]

        if len(past_days) == 0:
            # Cold start fallback: default baseline participation rate (~75% turnout)
            pred_bf = int(total_students * 0.70)
            pred_lunch = int(total_students * 0.85)
            pred_dinner = int(total_students * 0.80)
        else:
            # Weighted average favoring recent days
            weights = np.exp(np.linspace(-1, 0, len(past_days)))
            weights /= weights.sum()

            pred_bf = int(np.sum(bf_counts[past_days] * weights))
            pred_lunch = int(np.sum(lunch_counts[past_days] * weights))
            pred_dinner = int(np.sum(dinner_counts[past_days] * weights))

        # Calculate ingredient requirements for forecasted turnout
        ingredients = {
            "BREAKFAST": {k: round(v * pred_bf, 2) for k, v in self.PER_STUDENT_PORTION["BREAKFAST"].items()},
            "LUNCH": {k: round(v * pred_lunch / 1000.0 if "_g" in k else v * pred_lunch, 2) for k, v in self.PER_STUDENT_PORTION["LUNCH"].items()},
            "DINNER": {k: round(v * pred_dinner / 1000.0 if "_g" in k else v * pred_dinner, 2) for k, v in self.PER_STUDENT_PORTION["DINNER"].items()},
        }

        # Waste reduction estimation (comparing optimized AI forecast vs 100% capacity cooking)
        unoptimized_waste_kg = round((total_students * 3 - (pred_bf + pred_lunch + pred_dinner)) * 0.35, 2)

        return {
            "target_day": target_day,
            "total_enrolled_students": total_students,
            "forecasted_attendance": {
                "breakfast": pred_bf,
                "lunch": pred_lunch,
                "dinner": pred_dinner,
                "total_daily_meals": pred_bf + pred_lunch + pred_dinner
            },
            "ingredient_requirements": ingredients,
            "waste_optimization": {
                "estimated_food_waste_prevented_kg": max(0.0, unoptimized_waste_kg),
                "estimated_daily_savings_inr": max(0, int(unoptimized_waste_kg * 85))
            }
        }
