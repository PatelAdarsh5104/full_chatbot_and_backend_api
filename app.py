from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from chatbot.functionality import *
from user.login import *
from chatbot.streaming_response import *


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


### routers
app.include_router(login_router)
app.include_router(gemini_model_route)
app.include_router(test_router)




@app.get("/")
def read_root():
    
    return {"Hello": "World"}



@app.get("/health_check")
def read_about():
    return {"health": "Great"}



@app.get("/main")
def read_main():
    return {"Main": "FastAPI"} 