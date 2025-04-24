from email.message import EmailMessage
import smtplib
import ssl
from datetime import datetime

EMAIL_SENDER = "xayari229@gmail.com"
EMAIL_PASSWORD = "rkoa zvwu nqnj nifo"
EMAIL_RECEIVER = "xayari229@gmail.com"


def email_worker(task_queue):
    
    context = ssl.create_default_context()
    while True:
        task = task_queue.get()
        if task is None:  # Sentinel value to exit
            break
        
        image_path, current_time = task
        try:
            msg = EmailMessage()
            msg["Subject"] = "Intruder Alert!"
            msg["From"] = EMAIL_SENDER
            msg["To"] = EMAIL_RECEIVER
            msg.set_content("An unknown person was detected while you were away. Image attached.")
            #to Base64
            with open(image_path, "rb") as f:
                img_data = f.read()
                msg.add_attachment(img_data, maintype='image', subtype='jpeg', filename="intruder.jpg")
            
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
                smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
                smtp.send_message(msg)
            
            print(f"Intruder detected! Alert sent at {datetime.fromtimestamp(current_time)}")
        except Exception as e:
            print(f"Error sending email: {e}")
        finally:
            task_queue.task_done()
