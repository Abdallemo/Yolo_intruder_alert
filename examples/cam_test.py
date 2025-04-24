import cv2

# Try camera indexes from 0 to 5
for index in range(5):
    cap = cv2.VideoCapture(index)
    if cap.read()[0]:
        print(f"✅ Camera found at index {index}")
        cap.release()
    else:
        print(f"❌ No camera at index {index}")
