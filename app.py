from fastapi import FastAPI
from main import *
from functionality import *
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


### routers
app.include_router(main) 
app.include_router(gemini_model_route) # type: ignore




@app.get("/")
def read_root():
    
    return {"Hello": "World"}



@app.get("/health_check")
def read_about():
    return {"health": "Great"}