import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))


if getattr(sys, 'frozen', False):

    base_path = os.path.dirname(sys.executable)


    sys.path.append(os.path.join(base_path, 'src'))
else:
    base_path = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(os.path.join(base_path, 'src'))


if __name__ == "__main__":

    import cv2
    from queue import Queue
    from ultralytics import YOLO
    import threading
    from email_server import email_worker
    from camera import camera_setup

    YOUR_MODEL_PATH = os.path.join(base_path,'Models','last.pt')
    PRETRAINED_MODEL =  os.path.join(base_path,'Models','yolo11s.pt')

    print('current yolo path:'+YOUR_MODEL_PATH)

    my_model = YOLO(YOUR_MODEL_PATH)  
    model_yolo = YOLO(PRETRAINED_MODEL)  

    task_queue = Queue()
    cap = cv2.VideoCapture(0)
    # Start the worker thread

    worker_thread = threading.Thread(target=email_worker,args=(task_queue,))
    worker_thread.daemon = True
    worker_thread.start()

    try:
        camera_setup(cap,task_queue,my_model,model_yolo)
    except:
        KeyboardInterrupt
        print('exit 0')
    finally:
        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
        task_queue.put(None)  
        worker_thread.join()