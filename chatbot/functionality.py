import google.generativeai as genai
import os
from dotenv import load_dotenv
load_dotenv()
from fastapi import APIRouter
from pydantic import BaseModel

gemini_model_route = APIRouter(tags=["gemini_chatbot"])


class Input(BaseModel):
  question: str
  user: str = None
  system_instruction: str = "You are a helpful assistant."




model_options = ["gemini-2.0-flash-exp", "gemini-1.5-flash", "gemini-1.5-flash-8b","gemini-1.5-pro"]

gloabl_chat_history = []


def get_gemini_response(question, system_instructions):
    
    genai.configure(api_key=os.getenv("GENAI_API_KEY"))
    model = genai.GenerativeModel(model_name=model_options[0],  system_instruction=system_instructions)
    chat = model.start_chat(
            history=gloabl_chat_history
    )
    # chat = load_chat_history()

    response = chat.send_message(question)
    return response.text



@gemini_model_route.post("/gemini")
def call_gemini(input: Input):
    try:
      if not input.question:
        return {"success": False,"message": "question is required","response": None}
      if not input.system_instruction:
        return {"success": False,"message": "system_instruction is required","response": None}
      
      
      global gloabl_chat_history

      gloabl_chat_history.append({"role": "user", "parts": input.question})
      response = get_gemini_response(input.question, input.system_instruction)
      gloabl_chat_history.append({"role": "model", "parts": response})

      return {"success": True,"message": None,"response": response}
    
    except Exception as e:
      return {"success": False,"message": str(e),"response": None}