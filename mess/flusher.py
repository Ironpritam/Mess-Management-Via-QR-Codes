import csv
from datetime import date
from myapp.models import Student  # Replace 'myapp' with the actual name of your Django app

# Function to convert meal_data string to CSV format
def convert_meal_data(meal_data):
    return [int(digit) for digit in meal_data]

# Get all students
students = Student.objects.all()

# CSV file path
csv_file_path = 'student_data.csv'

# Open CSV file for writing
with open(csv_file_path, 'w', newline='') as csv_file:
    # Create a CSV writer
    csv_writer = csv.writer(csv_file)

    # Write header row
    header = ['Name', 'QR Code', 'Password', 'Meal Data']
    csv_writer.writerow(header)

    # Write student data
    for student in students:
        # Convert meal_data to CSV format
        meal_data_csv = convert_meal_data(student.meal_data)

        # Write student details to CSV file
        csv_writer.writerow([student.name, student.qr_code, student.password, meal_data_csv])

# Set meal_data to "0"*31 for all students
students.update(meal_data="0"*31)

print(f'Data flushed to CSV file: {csv_file_path}')
