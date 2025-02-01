import os
from dotenv import load_dotenv
load_dotenv()
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import random

async def send_otp(email_address):

    mail_paswords = os.getenv("mail_paswords")
    otp = random.randint(100000, 999999)

    # Email configuration
    from_address = os.getenv("from_email_address") # Replace with your Gmail address
    to_address = email_address  # Replace with the recipient's email address

    # Create message container
    msg = MIMEMultipart()
    msg['From'] = from_address
    msg['To'] = to_address
    msg['Subject'] = "Login OTP from Botai"

    # Create the body of the email
    body = "Your OTP is: " + str(otp)
    msg.attach(MIMEText(body, 'plain'))

    # Sending the email
    try:
        # Set up the server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Upgrade the connection to a secure encrypted SSL/TLS connection
        
        # Log in to your account
        server.login(from_address, mail_paswords)
        
        # Send the email
        server.sendmail(from_address, to_address, msg.as_string())
        
        print("Email sent successfully!")
        return otp
    
    except Exception as e:
        print(f"Failed to send email: {e}")
    finally:
        server.quit()  # Terminate the SMTP session