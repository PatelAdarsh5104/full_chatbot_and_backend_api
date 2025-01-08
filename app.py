from fastapi import FastAPI
from route import router
from main import *

app = FastAPI()

app.include_router(router)
app.include_router(main) # type: ignore

@app.get("/")
def read_root():
    
    return {"Hello": "World"}

@app.get("/about")
def read_about():
    return {"About": "FastAPI"}