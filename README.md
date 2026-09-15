# SmartMess AI: Edge CV & Predictive Analytics Mess Management System

> AI-enabled institutional dining management system combining edge computer vision, meal tracking and demand forecasting platform developed at **IIT Ropar**. Features edge QR-pass authentication, multi-backend low-light computer vision decoders, $O(1)$ bitwise meal tracking & anti-fraud verification, AI food waste demand forecasting, FastAPI REST microservices, and interactive vendor management dashboards.

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Django 4.2](https://img.shields.io/badge/Django-4.2%2B-092E20.svg)](https://www.djangoproject.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-REST%20Microservice-009688.svg)](https://fastapi.tiangolo.com/)
[![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-green.svg)](https://opencv.org/)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📌 Problem Statement & Executive Overview

Large institutional dining halls (such as university messes, corporate cafeterias, and industrial canteens) face three major operational bottlenecks:

1. **Queue Bottlenecks & Slow Validation**: Traditional paper registers or manual ID verification create long meal queues during peak hours.
2. **Meal Fraud & Double-Dipping**: Lack of real-time sync allows students or staff to claim multiple meals within the same window.
3. **Massive Food Wastage**: Mess managers cook static quantities without predictive turnout insights, resulting in significant monetary loss and unconsumed food waste.

Developed as a semester innovation project during studies at the **Indian Institute of Technology (IIT) Ropar**, **SmartMess AI** solves these challenges by combining **Edge Computer Vision**, **Bitwise Compressed Storage Architecture**, and **Predictive Machine Learning Demand Forecasting**.

```text
  +-----------------------+      +--------------------------+      +---------------------------+
  |  Edge Camera / Mobile | ---> | Multi-Backend CV Engine  | ---> | Bitwise Meal Verification |
  |   Vendor Terminal     |      | (OpenCV + PyZbar + CLAHE)|      |  (O(1) Bitmask State)     |
  +-----------------------+      +--------------------------+      +---------------------------+
                                                                                 |
                                                                                 v
  +-----------------------+      +--------------------------+      +---------------------------+
  | Automated CSV & Audit | <--- |  FastAPI REST / Django   | <--- |   AI Demand & Food Waste  |
  |    Export Reports     |      |   Vendor & Manager UI    |      |    Forecasting Engine     |
  +-----------------------+      +--------------------------+      +---------------------------+
```

---

## 🚀 Key Features & System Capabilities

### 📷 1. Edge Computer Vision QR Scanner (`vision_engine/`)
* **Multi-Backend Fallback Engine**: Combines **OpenCV `QRCodeDetector`** and **`PyZbar`** for multi-layered scanning resilience.
* **Low-Light & Blurry Image Preprocessing**: Automatically applies **CLAHE (Contrast Limited Adaptive Histogram Equalization)** and **Otsu Thresholding** variants to successfully decode blurred, rotated, or low-contrast mobile screenshot QR codes.
* **Stream & File Ingestion**: Accepts raw image bytes, uploaded files, or live camera frames.

### ⚡ 2. High-Efficiency Bitwise Meal Tracking Engine (`mess/models.py`)
* Compresses a full month (31 days) of meal attendance into a compact 31-character bitmask string stored in database records.
* **Bitwise Meal Bitmask Encoding**:
  * $\text{Breakfast} = 2^0 = 1$ (Bit 0)
  * $\text{Lunch} = 2^1 = 2$ (Bit 1)
  * $\text{Dinner} = 2^2 = 4$ (Bit 2)
* Enables instant **$O(1)$ Bitwise AND (`&`)** meal consumption checks and **Bitwise OR (`|`)** updates, completely eliminating duplicate meal consumption fraud.

### 📊 3. Predictive AI Food Waste & Demand Forecaster (`analytics_engine/`)
* **Turnout Analytics Model**: Analyzes historical attendance matrices to predict upcoming meal turnout for Breakfast, Lunch, and Dinner.
* **Automated Ingredient Requirement Estimator**: Translates turnout forecasts into exact raw ingredient quantities (e.g., Rice in kg, Flour in kg, Milk in L) to optimize kitchen procurement.
* **Sustainability & Cost Impact**: Quantifies estimated daily food waste prevented (in kg) and monetary savings (in INR).

### 🔌 4. Enterprise REST API Microservice (`api_server.py`)
* Built with **FastAPI** and **Pydantic** for seamless integration with IoT vendor hardware and mobile POS terminals.
* Provides `/api/v1/scan-qr` for real-time validation and `/api/v1/analytics/forecast` for demand insights.
* Self-documenting interactive OpenAPI / Swagger UI at `http://localhost:8001/docs`.

### 🖥️ 5. Modern Glassmorphism Web Portal (`mess/`)
* Responsive, dark-mode user interface for Vendor QR Scanning, Student Digital Pass Generation, and Mess Manager Analytics.

---

## 🧮 Bitwise Storage & Algorithmic Design

For any day $d \in \{1, 2, \dots, 31\}$, the meal consumption state $S_d$ is represented as an integer bitmask:

$$S_d = b_{\text{breakfast}} \cdot 1 + b_{\text{lunch}} \cdot 2 + b_{\text{dinner}} \cdot 4$$

Where $b_m \in \{0, 1\}$.

### Meal Validation Bitwise Rule
To check if student $i$ has consumed meal flag $M \in \{1, 2, 4\}$ on day $d$:

$$\text{HasEaten}(i, d, M) = \begin{cases} \text{True} & \text{if } (S_d \ \& \ M) > 0 \\ \text{False} & \text{otherwise} \end{cases}$$

### State Transition Bitwise Update
When meal $M$ is served, the updated state $S'_d$ is calculated via bitwise OR:

$$S'_d = S_d \ \mid \ M$$

This mathematical representation guarantees zero state corruption, negligible database storage footprint, and microsecond validation speeds.

---

## 🛠️ Technology Stack

| Domain | Technology | Purpose |
|---|---|---|
| **Computer Vision** | OpenCV, PyZbar, NumPy | Multi-backend QR extraction, CLAHE contrast enhancement & image preprocessing |
| **Web Framework** | Django 4.2 | Core application server, ORM data model, and session management |
| **Microservice API** | FastAPI, Uvicorn, Pydantic | High-performance REST microservice for IoT scanners & OpenAPI docs |
| **AI & Analytics** | NumPy, Scikit-Learn | Historic attendance parsing, turnout forecasting, and food waste modeling |
| **User Interface** | HTML5, CSS3 Glassmorphism | Dark-mode interactive vendor & analytics manager dashboards |
| **DevOps & Packaging** | Docker, Docker-Compose | Containerized multi-service deployment |

---

## 📁 Repository Layout

```text
Mess-Management-Via-QR-Codes-main/
├── README.md                           # Main Portfolio & Project Documentation
├── manage.py                           # Django Project Management Script
├── main.py                             # Unified CLI Launcher (Web, API, CLI Scanner, Forecast)
├── api_server.py                       # FastAPI REST Microservice for Edge Terminals
├── requirements.txt                    # Python Dependency Specifications
├── Dockerfile                          # Multi-stage Container Build File
├── docker-compose.yml                  # Full Stack Web & API Orchestration
│
├── vision_engine/                      # Computer Vision Engine Package
│   ├── __init__.py
│   └── qr_detector.py                  # Multi-Backend Decoder (OpenCV + PyZbar + CLAHE)
│
├── analytics_engine/                   # AI Analytics & Forecasting Package
│   ├── __init__.py
│   ├── meal_forecaster.py              # ML Turnout & Ingredient Demand Forecasting Engine
│   └── report_generator.py             # CSV Data Exporter & Analytics Summarizer
│
├── mess_manage/                        # Django System Settings & Configurations
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── mess/                               # Main Application & Business Logic
│   ├── models.py                       # Student & MealTransaction Audit Models
│   ├── views.py                        # Web Controllers (Scan, Auth, Analytics)
│   ├── qr.py                           # QR Proxy Interface
│   ├── flusher.py                      # Monthly Data Flush Runner
│   └── templates/                      # Glassmorphism HTML Dashboards
│
├── data/                               # Database Storage (SQLite db.sqlite3)
├── reports/                            # Generated Monthly CSV Audit Exports
└── qr_codes/                           # Generated Digital Student QR Passes
```

---

## ⚡ Quickstart Guide

### 1. Local Environment Setup

```bash
# Clone repository
git clone https://github.com/PritamMahajan/Mess-Management-Via-QR-Codes.git
cd Mess-Management-Via-QR-Codes

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
python manage.py makemigrations mess
python manage.py migrate
```

### 2. Launch Services via Unified CLI (`main.py`)

#### Launch Django Web Portal
```bash
python main.py --web
```
*Access Web Portal at `http://localhost:8000`*

#### Launch FastAPI Microservice
```bash
python main.py --api
```
*Access Swagger Interactive API Docs at `http://localhost:8001/docs`*

#### Run CLI QR Scanner on an Image File
```bash
python main.py --scan qr_codes/pritam.png
```

#### Run AI Demand Forecast in Terminal
```bash
python main.py --forecast
```

#### Export Monthly Data & Reset Bitmasks
```bash
python main.py --export
```

### 3. Launch via Docker Containerization

```bash
docker-compose up --build
```

---

## 📡 REST API Microservice Specification

### 1. Edge QR Meal Scan (`POST /api/v1/scan-qr`)

**Request Payload**: `multipart/form-data` containing image file `file`.

**Sample Python Client Request**:
```python
import requests

url = "http://localhost:8001/api/v1/scan-qr"
files = {"file": open("qr_codes/pritam.png", "rb")}

response = requests.post(url, files=files)
print(response.json())
```

**Response Output**:
```json
{
  "status": "SUCCESS",
  "message": "Meal recorded for pritam (LUNCH).",
  "student_name": "pritam",
  "meal_type": "LUNCH",
  "decoded_qr_data": "pritam",
  "detection_backend": "OpenCV-QRCodeDetector (Variant 1)"
}
```

---

## 👤 Author & Academic Background

* **Pritam Sunil Mahajan**
  * **M.Tech in Artificial Intelligence** — *Indian Institute of Technology (IIT) Ropar*
  * **B.Tech in Computer Engineering** — *Ramrao Adik Institute of Technology, D.Y. Patil Deemed to be University*
  * **Core Competencies**: Artificial Intelligence, Computer Vision, Edge ML Microservices, Software Architecture.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
