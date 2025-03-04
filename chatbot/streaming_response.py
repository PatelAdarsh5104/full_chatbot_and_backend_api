import json
import asyncio
from google import genai
import os
from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi import APIRouter
from pydantic import BaseModel


class Question(BaseModel):
    question: str

test_router = APIRouter(tags=["test"], prefix="/test")

def format_shadcn_response(text_chunk: str, index: int = 0):
    """Formats response chunks according to shadcn-chatbot-kit protocol"""
    return f'{index}:"{text_chunk}"\n'

def format_final_metadata():
    """Generates required ending metadata objects"""
    return (
        'e:' + json.dumps({
            "finishReason": "stop",
            "usage": {"promptTokens": None, "completionTokens": None},
            "isContinued": False
        }) + '\n'
        'd:' + json.dumps({
            "finishReason": "stop", 
            "usage": {"promptTokens": None, "completionTokens": None}
        }) + '\n'
    )

def get_streaming_response(question: str):
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    chat = client.chats.create(model="gemini-2.0-flash")
    
    response = chat.send_message_stream(question)
    for idx, chunk in enumerate(response):
        yield format_shadcn_response(chunk.text, idx)
    
    yield format_final_metadata()


@test_router.post("/streaming")
async def streaming_endpoint(questions: Question):
    return StreamingResponse(
        get_streaming_response(questions.question),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )
