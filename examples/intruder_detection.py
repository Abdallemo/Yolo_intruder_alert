import cv2
import smtplib
import ssl
from email.message import EmailMessage
import time
import os
from datetime import datetime
from ultralytics import YOLO

# --- CONFIGURATION ---
YOUR_MODEL_PATH = 'best.pt'
PRETRAINED_MODEL = "yolo11s.pt"  # Standard YOLO model for person detection
EMAIL_SENDER = "xayari229@gmail.com"
EMAIL_PASSWORD = "rkoa zvwu nqnj nifo"
EMAIL_RECEIVER = "xayari229@gmail.com"
DETECTION_INTERVAL = 120  # Seconds between email alerts

# --- LOAD MODELS ---
try:
    print("Loading custom model...")
    model_hatim = YOLO(YOUR_MODEL_PATH)
    
    print("Loading pretrained model...")
    model_yolo = YOLO(PRETRAINED_MODEL)
    
    print("Models loaded successfully!")
except Exception as e:
    print(f"Error loading models: {e}")
    exit()

# Print class names for debugging
print("Custom model classes:", model_hatim.names)
print("YOLO model classes:", model_yolo.names)

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
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")

# --- CAMERA SETUP ---
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

last_alert_time = time.time()
print("System is running... Press 'q' to stop.")

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break

        # Run inference - combine both detections
        results_combined = model_yolo(frame, verbose=False)
        results_hatim = model_hatim(frame, verbose=False)

        # Initialize detection flags
        hatim_detected = False
        person_detected = False

        # Check for your custom class (replace "Hatim" with your actual class name)
        for result in results_hatim:
            for box in result.boxes:
                if model_hatim.names[int(box.cls)] == "Hatim":  # Use your class name here
                    hatim_detected = True
                    break

        # Check for persons (class 0 in YOLO)
        for result in results_combined:
            for box in result.boxes:
                if int(box.cls) == 0:  # Person class
                    person_detected = True
                    # Draw red rectangle for intruders
                    if not hatim_detected:
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)

        # Show frame with detections
        cv2.imshow("Surveillance", frame)

        # Intruder alert logic
        if person_detected and not hatim_detected:
            current_time = time.time()
            if current_time - last_alert_time > DETECTION_INTERVAL:
                snapshot_path = f"intruder_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                cv2.imwrite(snapshot_path, frame)
                send_email(snapshot_path)
                last_alert_time = current_time
                print(f"Intruder detected! Alert sent at {datetime.now()}")

        # Exit on 'q' key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except Exception as e:
    print(f"Error during execution: {e}")

finally:
    cap.release()
    cv2.destroyAllWindows()
    print("System stopped.")