import cv2
from ultralytics import YOLO
import smtplib
import ssl
from email.message import EmailMessage
import time
from datetime import datetime

# defining the variables
YOUR_MODEL_PATH = '.\Models\last.pt' # Your custom trained model
PRETRAINED_MODEL = 'yolo11n.pt'  # Standard YOLO for person detection
EMAIL_SENDER = "xayari229@gmail.com"
EMAIL_PASSWORD = "rkoa zvwu nqnj nifo"
EMAIL_RECEIVER = "xayari229@gmail.com"
DETECTION_INTERVAL = 30  # Seconds between email alerts

# Loading modules
my_model = YOLO(YOUR_MODEL_PATH)  # Your custom model (detects you)
model_yolo = YOLO(PRETRAINED_MODEL)   # General person detection

# --- EMAIL FUNCTION ---
def send_email(image_path):
    msg = EmailMessage()
    msg["Subject"] = "Intruder Alert!"
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER
    msg.set_content("An unknown person was detected while you were away. Image attached.")
    
    with open(image_path, "rb") as f:
        img_data = f.read()
        msg.add_attachment(img_data, maintype='image', subtype='jpeg', filename="intruder.jpg")
    
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
        smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
        smtp.send_message(msg)

# --- CAMERA SETUP ---
cap = cv2.VideoCapture(0)
last_alert_time = time.time()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # First check for yourself using custom model
    results_hatim = my_model(frame, verbose=False)
    hatim_detected = len(results_hatim[0].boxes) > 0

    # Then check for general people only if you're not detected
    intruder_detected = False
    if not hatim_detected:
        results_yolo = model_yolo(frame, verbose=False)
        for r in results_yolo:
            for box in r.boxes:
                if int(box.cls[0]) == 0:  # Class 0 is 'person' in YOLO
                    intruder_detected = True
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    confidence = box.conf[0]
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    label = f'Intruder: {confidence:.2f}'
                    cv2.putText(frame, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    # Draw your detection (green box)
    for r in results_hatim:
        for box in r.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            confidence = box.conf[0]
            class_name = my_model.names[int(box.cls[0])]
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            label = f'{class_name}: {confidence:.2f}'
            cv2.putText(frame, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Intruder alert logic (only when you're not detected)
    if intruder_detected and not hatim_detected:
        current_time = time.time()
        if current_time - last_alert_time > DETECTION_INTERVAL:
            snapshot_path = f"intruder_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            cv2.imwrite(snapshot_path, frame)
            send_email(snapshot_path)
            last_alert_time = current_time
            print(f"Intruder detected! Alert sent at {datetime.now()}")

    cv2.imshow('Surveillance System', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()