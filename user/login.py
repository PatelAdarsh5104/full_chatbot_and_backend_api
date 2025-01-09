from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from user.database_operations import signup_user ,query_get_all_user_details

login_router = APIRouter(tags=["login"])

class User(BaseModel):
    username: str
    password: str
    email: str
    phone: str


@login_router.post("/login")
async def sign_in(user: User):

    try:
        response = await signup_user(user.username, user.email, user.password, user.phone)
        if response["message"] == "user sign in successfully.":
            response["error"] = None
            return response
    except Exception as e:
        
        return {"message": "An error occurred while logging in.", "error": str(e),"user_id": None}


@login_router.get("/list_all_users")
async def list_all_users():
    try:
        response = await query_get_all_user_details()
        print(type(response),response)
        return response
    except Exception as e:
        return {"message": "An error occurred while retrieving data.", "error": str(e)}