import cv2
import time
from datetime import datetime
from PIL import Image,ImageTk

DETECTION_INTERVAL = 30  # Seconds between email alerts



def camera_setup(cap:cv2.VideoCapture,task_queue, my_model,model_yolo,VideoLable):
    print('Starting Camera Setup ')
    last_alert_time = time.time()

    ret, frame = cap.read()
    if not ret:
        print('something Went')
        return

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
            snapshot_path = f"./alert_images/intruder_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            # Save image in main thread 
            cv2.imwrite(snapshot_path, frame)
            # Add email task to queue
            task_queue.put((snapshot_path, current_time))
            last_alert_time = current_time

    #cv2.imshow('Surveillance System', frame)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(frame_rgb)
    imgtk = ImageTk.PhotoImage(image=img)

    VideoLable.imgtk = imgtk
    VideoLable.configure(image=imgtk)

    VideoLable.after(10, camera_setup, cap, task_queue, my_model, model_yolo,VideoLable)
