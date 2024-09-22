from django.db import models

# Create your models here.
from django.db import models

class Student(models.Model):
    name = models.CharField(max_length=100)
    qr_code = models.CharField(max_length=100)  # QR code details
    password = models.CharField(max_length=50)  # Password for the student
    meal_data = models.CharField(max_length=32)  

    # Other student-related fields like ID, class, etc.
    def __str__(self):
        return self.name