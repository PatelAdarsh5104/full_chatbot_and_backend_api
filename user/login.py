from fastapi import APIRouter, Request
from pydantic import BaseModel, EmailStr
from user.database_operations import signup_user ,query_get_all_user_details, logout_session, login_and_manage_session , send_otp_functionality, varify_opt_function
from utilities.jwt_token import generate_jwt
import os , logging

login_router = APIRouter(tags=["login & Signup"], prefix="/user")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

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

class User_model(BaseModel):
    user_id: str
    user_name: str
    user_email: str

class VarifyOtp_model(BaseModel):
    email: EmailStr
    opt: int

class send_otp_model(BaseModel):
    email: EmailStr


### Signup
@login_router.post("/signup")
async def sign_in(user: signup_user_model):
    try:
        # Perform signup
        response = await signup_user(user.user_name, user.email, user.password, user.phone, user.name)
        logger.info(f"User name: {user.user_name}, Api: signup")
        return {"success": True, "message": None, "data": response}

    except Exception as e:
        return {"success": False, "message": str(e), "data": None}


### Login
@login_router.post("/login")
async def login_function(user: LoginRequest_model):
    try:
        # Call the combined login and session management function
        response = await login_and_manage_session(user.user_name, user.password)
        logger.info(f"User name: {user.user_name}, Api: login")
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

        logger.info(f"User ID: {user.user_id}, Api: logout")
        return {"success":True,"message":None,"data":response}
    
    except Exception as e:
        return {"success":False,"message": str(e),"data":None}


@login_router.post("/generate/jwt")
async def generate_jwt_function(user: User_model):
    try:
        # Generate JWT token
        token = await generate_jwt(user.user_id, user.user_name, user.user_email)

        logger.info(f"User ID: {user.user_id}, Api: generate_jwt")
        return {"success":True,"message":None,"data":{"token": token}}
    except Exception as e:
        return {"success":False,"message": str(e),"data":None}
    



@login_router.post("/login/send-otp")
async def sign_in_with_email(user: send_otp_model):
    try:
        if  user.email is None:
            raise Exception("Email cannot be None")
    
        response = await send_otp_functionality(user.email)

        logger.info(f"User name: {user.email}, Api: login with email")
        return {"success": True, "message": None, "data": response}

    except Exception as e:
        return {"success": False, "message": str(e), "data": None}
    

@login_router.post("/login/verify-otp")
async def verify_otp(user: VarifyOtp_model):
    try:

        response = await varify_opt_function(user.email, user.opt)

        logger.info(f"User name: {user.email}, Api: verify otp")
        return {"success": True, "message": None, "data": response}
    
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}
    


@login_router.get("/get-ip")
async def get_ip(request: Request):
    try:
        ip_address = request.client.host
        port = request.client.port
        logger.info(f"IP Address: {ip_address}, Api: get_ip, port:{port}")
        return {"success": True, "message": None, "data": {"ip_address": ip_address, "port": port}}
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}