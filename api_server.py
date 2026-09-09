"""
FastAPI Microservice for SmartMess AI.
Provides high-performance RESTful API endpoints for IoT vendor terminals, edge devices, and AI analytics.
"""
import os
import sys
import django
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Initialize Django environment for ORM queries
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mess_manage.settings')
django.setup()

from mess.models import Student, MealTransaction
from mess.views import classify_meal_type
from vision_engine.qr_detector import detect_and_decode_qr
from analytics_engine.meal_forecaster import MealForecaster

app = FastAPI(
    title="SmartMess AI - Edge Microservice",
    description="RESTful API microservice for Computer Vision QR scanning, meal validation, and ML turnout forecasting.",
    version="2.0.0"
)

# Enable CORS for cross-origin web/IoT clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ScanResponse(BaseModel):
    status: str
    message: str
    student_name: Optional[str] = None
    meal_type: Optional[str] = None
    decoded_qr_data: Optional[str] = None
    detection_backend: Optional[str] = None


@app.get("/api/v1/health")
def health_check():
    return {
        "status": "HEALTHY",
        "system": "SmartMess AI Edge API",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/v1/scan-qr", response_model=ScanResponse)
async def scan_qr_endpoint(file: UploadFile = File(...)):
    """
    Edge QR Scanner Endpoint for Vendor Terminals.
    Decodes QR image, validates meal window & double-eating bitmask, and logs audit trail.
    """
    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Empty file payload")

    qr_text, meta = detect_and_decode_qr(image_bytes)
    if not qr_text:
        return ScanResponse(
            status="FAILED",
            message="No valid QR code detected in image frame.",
            detection_backend=meta.get("error")
        )

    current_time = datetime.now()
    meal_type, meal_flag = classify_meal_type(current_time)
    if not meal_type or not meal_flag:
        return ScanResponse(
            status="REJECTED",
            message=f"Outside operating hours for mess meals (Time: {current_time.strftime('%H:%M')}).",
            decoded_qr_data=qr_text
        )

    try:
        student = Student.objects.get(name=qr_text)
        day_idx = current_time.day
        has_eaten = student.has_eaten_meal(day_idx, meal_flag)

        if not has_eaten:
            student.record_meal(day_idx, meal_flag)
            MealTransaction.objects.create(
                student=student,
                meal_type=meal_type,
                status="SUCCESS"
            )
            return ScanResponse(
                status="SUCCESS",
                message=f"Meal recorded for {student.name} ({meal_type}).",
                student_name=student.name,
                meal_type=meal_type,
                decoded_qr_data=qr_text,
                detection_backend=meta.get("backend")
            )

        MealTransaction.objects.create(
            student=student,
            meal_type=meal_type,
            status="ALREADY_SERVED"
        )
        return ScanResponse(
            status="ALREADY_SERVED",
            message=f"Warning: {student.name} has already consumed {meal_type} today.",
            student_name=student.name,
            meal_type=meal_type,
            decoded_qr_data=qr_text,
            detection_backend=meta.get("backend")
        )

    except Student.DoesNotExist:
        return ScanResponse(
            status="NOT_FOUND",
            message=f"Student identifier '{qr_text}' not registered in system.",
            decoded_qr_data=qr_text
        )


@app.get("/api/v1/analytics/forecast")
def get_meal_forecast(day: Optional[int] = None):
    """
    AI Predictive Analytics Endpoint.
    Returns forecasted attendance and ingredient requirements.
    """
    students_meal_data = list(Student.objects.values_list('meal_data', flat=True))
    forecaster = MealForecaster(students_meal_data)
    forecast_results = forecaster.forecast_meal_demand(target_day=day)
    return forecast_results


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=True)
