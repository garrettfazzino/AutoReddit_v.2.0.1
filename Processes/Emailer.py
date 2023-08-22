import smtplib
from email.message import EmailMessage
from datetime import datetime
from dotenv import load_dotenv
import os

"Email notifications for batches and errors during video creation"

# Notify via email that a batch is ready
def notify_email(gcs_folder=str):
    """Sends notification email to alert that a new video has been created.
    
gcs_folder:
    folder name returned form the gcs_upload function, denotes where to locate final cuts"""
    
    load_dotenv()
    sender_email = os.getenv('SENDER_EMAIL')
    sender_password = os.getenv('SENDER_PASSWORD')
    recipient_email = os.getenv('RECIPIENT_EMAIL')

    msg = EmailMessage()
    msg.set_content(f"""
    Hello Gablo, a new batch of videos has arrived in your Google Cloud Storage.
    
    Filename: {gcs_folder}

    Enjoy posting!

    """)

    msg['Subject'] = f'AutoReddit: {gcs_folder} {datetime.now()}'
    msg['From'] = sender_email
    msg['To'] = recipient_email

    # Send the message via our own SMTP server.
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(sender_email, sender_password)
    server.send_message(msg)
    server.quit()

    print("\nEmail update sent to < auto.everything.bot@gmail.com >\n")
    return True

# Email when an error occurs
def error_email(error, iteration_count=int, error_count=int):
    """Sends email to alert of errors occuring in creation of AutoReddit posts
    
error:
    The error which occurred during the Nth iteration
iteration_count:
    Denotes which iteration AutoReddit was on when the error occurred
error_count:
    Denotes how many errors have occurred during the current running process of AutoReddit

"""

    sender_email = "garrettfazzino@gmail.com"
    sender_password = "qwsjtxgiosjgkmst"
    recipient_email = "auto.everything.bot@gmail.com"

    msg = EmailMessage()
    msg.set_content(f"""
    Hello Gablo, there was a problem during iteraiton #{iteration_count} of the current AutoReddit operation.
    This is Error #{error_count} on the currently operating docker container. 
    At 10 errors, the image will automatically stop itself to prevent any damages from occurring.

    Error: {error}

    If this is a serious or repeating error, you should take immediate action to resolve the problem.

    Otherwise, please disregard.

    """)

    msg['Subject'] = f'AutoReddit Error Occurred #{iteration_count}'
    msg['From'] = sender_email
    msg['To'] = recipient_email

    # Send the message via our own SMTP server.
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(sender_email, sender_password)
    server.send_message(msg)
    server.quit()
    
    print("\nATTENTION: Error email sent to <auto.everything.bot@gmail.com>\n")
    return True
