import asyncio
import google.generativeai as genai
import os
from dotenv import load_dotenv
load_dotenv()
from fastapi import APIRouter
from pydantic import BaseModel
from chatbot.database_operations import insert_question_answer,get_chat_history_sql


gemini_model_route = APIRouter(tags=["gemini_chatbot"], prefix="/chat")


class Input(BaseModel):
  question: str
  user_id: str 
  session_id: str
  system_instruction: str = "You are a helpful assistant."


class chat_history_model(BaseModel):
  user_id: str 
  session_id: str





model_options = ["gemini-2.0-flash-exp", "gemini-1.5-flash", "gemini-1.5-flash-8b","gemini-1.5-pro"]


async def get_gemini_response(question, system_instructions, user_id, session_id):
    
    genai.configure(api_key=os.getenv("GENAI_API_KEY"))

    ### Get the old chat history
    full_history = await get_chat_history_sql(user_id=user_id, session_id=session_id)
  
    infunction_chat_history = []

    for i in full_history:
        infunction_chat_history.append({"role": "user", "parts": i["question"]})
        infunction_chat_history.append({"role": "model", "parts": i["answer"]})

    model = genai.GenerativeModel(model_name=model_options[2],  system_instruction=system_instructions)
    chat = model.start_chat(
            history=infunction_chat_history
    )
    # chat = load_chat_history()

    response = chat.send_message(question)
    return response.text



@gemini_model_route.post("/question_answer")
async def call_gemini(input: Input):
    
    try:
      if not input.question:
        return {"success": False,"message": "question is required","data": None}
      if not input.system_instruction:
        return {"success": False,"message": "system_instruction is required","data": None}
      
      response =await get_gemini_response(input.question, input.system_instruction,input.user_id,input.session_id)
      print(response)
      
      await insert_question_answer(user_id=input.user_id, session_id=input.session_id,question=input.question,answer=response)

      return {"success": True,"message": None,"data": response}
    
    except Exception as e:
      return {"success": False,"message": str(e),"data": None}
    

@gemini_model_route.post("/get_chat_history")
async def get_chat_history(chat: chat_history_model):
   try:
      full_history = await get_chat_history_sql(user_id=chat.user_id, session_id=chat.session_id)

      if not full_history:
        raise Exception("No chat history found.")
      
      return {"success": True,"message": None,"data": full_history}
   except Exception as e:
      return {"success": False,"message": str(e),"data": None}