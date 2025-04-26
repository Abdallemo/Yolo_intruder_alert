import sys
import os
import threading
from queue import Queue

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

if getattr(sys, 'frozen', False):
    base_path = os.path.dirname(sys.executable)
    sys.path.append(os.path.join(base_path, 'src'))
else:
    base_path = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(os.path.join(base_path, 'src'))


my_model = None
model_yolo = None

def load_models():
    global my_model, model_yolo
    from ultralytics import YOLO
    YOUR_MODEL_PATH = os.path.join(base_path, 'Models', 'last.pt')
    PRETRAINED_MODEL = os.path.join(base_path, 'Models', 'yolo11s.pt')
    
    print('Loading custom model...')
    my_model = YOLO(YOUR_MODEL_PATH)  
    
    print('Loading pretrained model...')
    model_yolo = YOLO(PRETRAINED_MODEL)  
    
    print('Models loaded successfully.')
    print('Current Threads : ',threading.active_count())

def on_closing():
    cap.release()
    rootWindowPanel.destroy()
    task_queue.put(None)
    worker_thread.join()

def check_models_loaded():
    if my_model is not None and model_yolo is not None:
        print("Models are loaded, setting up camera.")
        loading_label.pack_forget() 
        camera_setup(cap, task_queue, my_model, model_yolo, VideoLabel)
    else:
        rootWindowPanel.after(500, check_models_loaded) 

if __name__ == "__main__":
    import cv2
    from email_server import email_worker
    from camera import camera_setup
    import tkinter as tk
    from tkinter import ttk
    
    rootWindowPanel = tk.Tk()
    rootWindowPanel.title("Identity Detector")
    rootWindowPanel.geometry("800x600")

    loading_label = tk.Label(rootWindowPanel, text="Loading models, please wait...", font=("Arial", 20))
    loading_label.pack(pady=20)

    VideoLabel = tk.Label(rootWindowPanel)
    VideoLabel.pack()
    task_queue = Queue()
    cap = cv2.VideoCapture(0)
    
    worker_thread = threading.Thread(target=email_worker, args=(task_queue,))
    worker_thread.daemon = True
    worker_thread.start()

    model_thread = threading.Thread(target=load_models)
    model_thread.start()
    
 
    rootWindowPanel.after(500, check_models_loaded)

    rootWindowPanel.protocol("WM_DELETE_WINDOW", on_closing)
    rootWindowPanel.mainloop()
