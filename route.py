from fastapi import FastAPI, APIRouter

router = APIRouter(tags=["route"])


@router.get("/route")
def read_route():
    return {"Route": "FastAPI"}
 
@router.get("/route/get/user")
def read_route():
    return {"Route": "FastAPI"}

@router.get("/route/get/user/{user_id}")
def read_route(user_id: int):
    return {"Route": "FastAPI", "user_id": user_id}