import cv2
import numpy as np
import pyqrcode
import io
from typing import Tuple, Optional, Dict, Any

try:
    from pyzbar.pyzbar import decode as pyzbar_decode
    HAS_PYZBAR = True
except ImportError:
    HAS_PYZBAR = False


def preprocess_image_variants(img_np: np.ndarray):
    """
    Generate image preprocessing variants to improve QR code detection 
    under low-light, high-exposure, or blurry conditions.
    """
    variants = []
    
    # 1. Original image
    variants.append(img_np)
    
    # 2. Grayscale
    if len(img_np.shape) == 3:
        gray = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
    else:
        gray = img_np.copy()
    variants.append(gray)
    
    # 3. Contrast Normalization (CLAHE)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced_gray = clahe.apply(gray)
    variants.append(enhanced_gray)
    
    # 4. Otsu Thresholding
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    variants.append(thresh)
    
    return variants


def detect_and_decode_qr(image_input: Any) -> Tuple[Optional[str], Dict[str, Any]]:
    """
    Robust multi-backend QR code decoder.
    Supports file paths, bytes, Django InMemoryUploadedFile, and NumPy arrays.
    
    Returns:
        Tuple of (decoded_data_string, metadata_dict)
    """
    meta = {
        "success": False,
        "backend": None,
        "attempts": 0,
        "data": None
    }
    
    img_np = None
    
    # Load Image Array
    if isinstance(image_input, str):
        img_np = cv2.imread(image_input)
    elif isinstance(image_input, bytes):
        nparr = np.frombuffer(image_input, np.uint8)
        img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    elif hasattr(image_input, 'read'):
        # Handles Django InMemoryUploadedFile or BytesIO
        content = image_input.read()
        if hasattr(image_input, 'seek'):
            image_input.seek(0)
        nparr = np.frombuffer(content, np.uint8)
        img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    elif isinstance(image_input, np.ndarray):
        img_np = image_input
        
    if img_np is None or img_np.size == 0:
        meta["error"] = "Invalid or empty image payload"
        return None, meta
        
    variants = preprocess_image_variants(img_np)
    detector = cv2.QRCodeDetector()
    
    # Attempt 1: OpenCV QRCodeDetector across preprocessed variants
    for idx, var in enumerate(variants):
        meta["attempts"] += 1
        data, vertices, _ = detector.detectAndDecode(var)
        if data and len(data.strip()) > 0:
            meta["success"] = True
            meta["backend"] = f"OpenCV-QRCodeDetector (Variant {idx+1})"
            meta["data"] = data.strip()
            return meta["data"], meta
            
    # Attempt 2: PyZbar (if available) across variants
    if HAS_PYZBAR:
        for idx, var in enumerate(variants):
            meta["attempts"] += 1
            decoded_objects = pyzbar_decode(var)
            for obj in decoded_objects:
                qr_text = obj.data.decode("utf-8").strip()
                if qr_text:
                    meta["success"] = True
                    meta["backend"] = f"PyZbar (Variant {idx+1})"
                    meta["data"] = qr_text
                    return meta["data"], meta
                    
    meta["error"] = "No valid QR code detected in image"
    return None, meta


def generate_qr_code(data: str, output_file_path: Optional[str] = None, scale: int = 6) -> Any:
    """
    Generate QR code using PyQRCode.
    Optionally saves to PNG file path or returns PyQRCode object.
    """
    qr = pyqrcode.create(data)
    if output_file_path:
        qr.png(output_file_path, scale=scale)
    return qr
