from fastapi import APIRouter

main = APIRouter(tags=["main"])

@main.get("/main")
def read_main():
    return {"Main": "FastAPI"}

@main.get("/main/get/user")
def read_main():
    return {"Main": "FastAPI"}