from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from user.database_operations import signup_user ,query_get_all_user_details, login_user,dublicate_user,sessionid_generate, logout_session
import bcrypt

login_router = APIRouter(tags=["login & Signup"], prefix="/user")

class signup_user_model(BaseModel):
    user_name: str
    password: str
    email: EmailStr
    phone: str = None


class LoginRequest_model(BaseModel):
    user_name: str
    password: str

class LogoutRequest_model(BaseModel):
    user_id: str

@login_router.post("/signup")
async def sign_in(user: signup_user_model):
    try:
        ## Check if the user_name is already exist or not
        dublicate_name = await dublicate_user(user.user_name)

        if dublicate_name:
            raise Exception("User already exist with this name.")
        
        hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())

        response = await signup_user(user.user_name, user.email, hashed_password, user.phone)

        return {"success":True,"message":None,"data":response}
        
    except Exception as e:
        return {"success":False,"message": str(e),"data":None}


@login_router.post("/login")
async def login_function(user: LoginRequest_model):
    try:

        response = await login_user(user.user_name)

        ### Check if the password is correct or not
        if not bcrypt.checkpw(user.password.encode('utf-8'), response["user_password"].encode('utf-8')):
            raise Exception("Invalid username or password.")
        
        session_id =await sessionid_generate(response["user_id"])
    
        return {"success":True,
                "message":None,
                "data": { 
                    "respose": "Login successful!",
                    "session_id": session_id, 
                    "user_id": response["user_id"], 
                    "user_name": response["user_name"], 
                    "user_email": response["user_email"]
                    }
                }

    except Exception as e:
        return {"success":False,
                "message": str(e),
                "data":None
                }


@login_router.get("/list_all_users")
async def list_all_users():
    try:
        response = await query_get_all_user_details()
        return {"success":True,"message":None,"data":response}
    except Exception as e:
        return {"success":False,"message": str(e), "data":None}
    

@login_router.post("/logout")
async def logout(user: LogoutRequest_model):
    try:
        response = await logout_session(user.user_id)

        return {"success":True,"message":None,"data":response}
    
    except Exception as e:
        return {"success":False,"message": str(e),"data":None}
