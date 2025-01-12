from fastapi import APIRouter
from pydantic import BaseModel, EmailStr
from user.database_operations import signup_user ,query_get_all_user_details, logout_session, login_and_manage_session

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
