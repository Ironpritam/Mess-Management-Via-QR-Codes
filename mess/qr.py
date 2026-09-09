"""
QR Processing Proxy for Mess App.
Delegates encoding and multi-backend decoding to vision_engine.
"""
from vision_engine.qr_detector import detect_and_decode_qr, generate_qr_code


def encode(data):
    return generate_qr_code(data)


def decode(qr_image):
    data, meta = detect_and_decode_qr(qr_image)
    if data:
        print(f"[SmartMess AI CV Engine] Decoded QR via {meta.get('backend')}: {data}")
        return data
    else:
        print(f"[SmartMess AI CV Engine] QR Decode failed: {meta.get('error')}")
        return None