import pyqrcode
import cv2
import numpy as np

def encode(data):
    qr_code = pyqrcode.create(data)
    # qr.png("/qr_dir/horn.png", scale=6)
    return qr_code

def decode(qr_image):
    # Convert the uploaded image from InMemoryUploadedFile to numpy array
    nparr = np.frombuffer(qr_image.read(), np.uint8)
    img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Convert from BGR to RGB if needed (depends on OpenCV version)
    img_np = cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB)

    detector = cv2.QRCodeDetector()
    data, vertices_array, binary_qrcode = detector.detectAndDecode(img_np)

    if vertices_array is not None:
        print("QRCode data:")
        print(data)
        return data
    else:
        print("There was some error in decoding the QR code")

    return None