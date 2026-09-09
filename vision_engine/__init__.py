"""
Vision Engine Module for SmartMess AI.
Provides multi-backend QR code detection, image pre-processing, and frame enhancement.
"""
from .qr_detector import detect_and_decode_qr, generate_qr_code

__all__ = ["detect_and_decode_qr", "generate_qr_code"]
