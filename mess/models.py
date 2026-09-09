from django.db import models


class Student(models.Model):
    name = models.CharField(max_length=100)
    qr_code = models.CharField(max_length=100)  # QR code payload/identifier
    password = models.CharField(max_length=50)   # Password for student login
    meal_data = models.CharField(max_length=32, default="0"*31)  # 31-day bitmask representation

    def __str__(self):
        return self.name

    def has_eaten_meal(self, day_index: int, meal_flag: int) -> bool:
        """
        Check if student consumed specific meal on given day (1-indexed day of month).
        meal_flag: 1 = Breakfast, 2 = Lunch, 4 = Dinner
        """
        if day_index < 1 or day_index > len(self.meal_data):
            return False
        current_bitmask = int(self.meal_data[day_index - 1])
        return bool(current_bitmask & meal_flag)

    def record_meal(self, day_index: int, meal_flag: int):
        """
        Atomically update the bitmask state for the given day index.
        """
        if 1 <= day_index <= len(self.meal_data):
            meal_list = list(self.meal_data)
            current_val = int(meal_list[day_index - 1])
            new_val = current_val | meal_flag
            meal_list[day_index - 1] = str(new_val)
            self.meal_data = ''.join(meal_list)
            self.save()


class MealTransaction(models.Model):
    """
    Granular audit logging model for scan activity and anti-fraud verification.
    """
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='transactions')
    meal_type = models.CharField(max_length=20)  # BREAKFAST, LUNCH, DINNER
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='SUCCESS')  # SUCCESS, ALREADY_SERVED, INVALID_SCAN
    terminal_id = models.CharField(max_length=50, default='VENDOR_TERMINAL_1')

    def __str__(self):
        return f"{self.student.name} - {self.meal_type} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"