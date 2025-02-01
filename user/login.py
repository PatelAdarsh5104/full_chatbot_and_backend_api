from fastapi import APIRouter
from pydantic import BaseModel, EmailStr
from user.database_operations import signup_user ,query_get_all_user_details, logout_session, login_and_manage_session , signup_user_email
import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os
load_dotenv()

login_router = APIRouter(tags=["login & Signup"], prefix="/user")

class signup_user_model(BaseModel):
    name : str
    user_name: str
    password: str
    email: EmailStr
    phone: str = None


class LoginRequest_model(BaseModel):
    user_name: str
    password: str

class LogoutRequest_model(BaseModel):
    user_id: str


### Signup
@login_router.post("/signup")
async def sign_in(user: signup_user_model):
    try:
        # Perform signup
        response = await signup_user(user.user_name, user.email, user.password, user.phone, user.name)
        return {"success": True, "message": None, "data": response}

    except Exception as e:
        return {"success": False, "message": str(e), "data": None}


### Login
@login_router.post("/login")
async def login_function(user: LoginRequest_model):
    try:
        # Call the combined login and session management function
        response = await login_and_manage_session(user.user_name, user.password)
        return {"success": True, "message": None, "data": response}
    
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}



### List all users
@login_router.get("/list_all_users")
async def list_all_users():
    try:
        response = await query_get_all_user_details()
        return {"success":True,"message":None,"data":response}
    except Exception as e:
        return {"success":False,"message": str(e), "data":None}
    

### Logout
@login_router.post("/logout")
async def logout(user: LogoutRequest_model):
    try:
        response = await logout_session(user.user_id)

        return {"success":True,"message":None,"data":response}
    
    except Exception as e:
        return {"success":False,"message": str(e),"data":None}


class signup_user_email_model(BaseModel):
    name : str
    email: EmailStr
    user_name: str
    phone: str = None

    
def send_otp(email_address):

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


@login_router.post("/signup/email")
async def sign_in_with_email(user: signup_user_email_model):
    try:
        if user.name is None and user.email is None:
            raise Exception("Name and Email cannot be None")
        
        otp = send_otp(user.email)

        response = await signup_user_email(user.user_name, user.email, otp, user.phone, user.name)
        return {"success": True, "message": None, "data": response}

    except Exception as e:
        return {"success": False, "message": str(e), "data": None}