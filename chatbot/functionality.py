# from google import genai
import asyncio
import google.generativeai as genai
import os
from dotenv import load_dotenv
load_dotenv()
from fastapi import APIRouter, Request
from pydantic import BaseModel
from chatbot.database_operations import insert_question_answer,get_chat_history_sql, create_bot, query_get_all_bot_details, update_bot_query, delete_bot_query
from utilities.jwt_token import jwt_required
from typing import Optional
import logging

gemini_model_route = APIRouter(tags=["gemini_chatbot"], prefix="/chat")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


class Input(BaseModel):
  question: str
  bot_id : str
  session_id: str
  system_instruction: str = "You are a helpful assistant."


class chat_history_model(BaseModel):
  bot_id : str


class BOTCREATE(BaseModel):
   bot_name: str
   bot_category: str
   bot_instruction: Optional[str] = None

class BOTUPDATEMODEL(BaseModel):
   bot_id: str
   bot_name: Optional[str] = None
   bot_category: Optional[str] = None
   bot_instruction: Optional[str] = None


model_options = ["gemini-2.0-flash-exp", "gemini-1.5-flash", "gemini-1.5-flash-8b","gemini-1.5-pro"]


async def get_gemini_response(question, system_instructions, user_id, bot_id):
    
    genai.configure(api_key=os.getenv("GENAI_API_KEY"))

    ### Get the old chat history
    full_history = await get_chat_history_sql(user_id=user_id, bot_id=bot_id)
  
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


async def generate_bot_instruction(bot_name, bot_category):
      from google import genai

      client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

      response = client.models.generate_content(
         model="gemini-2.0-flash",
         contents=[f"You are the senior Prompt Engineer, You have to generate a prompt for the personalized chatbot, for the generating prompt, I will provide you a the name of the Bot, and Category of the bot. From the name and category, you have to generate a Instruction for the chatbot, that how it should behave and the way it should interact with the user. The prompt should be short and specific. Name: {bot_name}, Category: {bot_category}, Do not add any extra text."],)

      return response.text


@gemini_model_route.post("/question_answer")
@jwt_required
async def call_gemini(request: Request,input: Input):
    
    try:
      if not input.question:
        return {"success": False,"message": "question is required","data": None}
      if not input.system_instruction:
        return {"success": False,"message": "system_instruction is required","data": None}
      
      user_payload = request.state.user
      user_id = user_payload.get("user_id")  # Assuming "user_id" is in the payload

      response =await get_gemini_response(input.question, input.system_instruction,user_id,input.bot_id)
      
      
      await insert_question_answer(user_id=user_id, session_id=input.session_id, bot_id = input.bot_id,question=input.question,answer=response)

      logger.info(f"User ID: {user_id}, Api: question_answer,  asked: {input.question}")

      return {"success": True,"message": None,"data": response}
    
    except Exception as e:
      return {"success": False,"message": str(e),"data": None}
    

@gemini_model_route.post("/get_chat_history")
@jwt_required
async def get_chat_history(request: Request,chat: chat_history_model,):
   try:
      
      user_payload = request.state.user
      user_id = user_payload.get("user_id")  

      full_history = await get_chat_history_sql(user_id=user_id, bot_id=chat.bot_id)

      if not full_history:
        raise Exception("No chat history found.")
      
      logger.info(f"User ID: {user_id}, Api: get_chat_history,  bot_id: {chat.bot_id}")
      return {"success": True,"message": None,"data": full_history}
   
   except ValueError as e:
      return {"success": False,"message": str(e),"data": None}
   except Exception as e:
      return {"success": False,"message": str(e),"data": None}
   

@gemini_model_route.post("/bot/create")
@jwt_required
async def bot_create(request: Request,bot: BOTCREATE):
   try:
      
      print("In bot create")
      user_payload = request.state.user
      user_id = user_payload.get("user_id")  # Assuming "user_id" is in the payload

      if bot.bot_instruction is None:
        bot.bot_instruction = await generate_bot_instruction(bot_name=bot.bot_name, bot_category=bot.bot_category)

      bot_id = await create_bot(user_id=user_id, bot_name=bot.bot_name,bot_category=bot.bot_category,bot_instruction=bot.bot_instruction)
      
      logger.info(f"User ID: {user_id}, Api: bot_create,  bot_id: {bot_id}")
      return {"success": True,"message": None,"data": {"bot_id": bot_id, "user_id": user_id, "bot_name": bot.bot_name, "bot_category": bot.bot_category, "bot_instruction": bot.bot_instruction}}
   
   except ValueError as e:
      return {"success": False,"message": str(e),"data": None}
   except Exception as e:
      return {"success": False,"message": str(e),"data": None}
   

@gemini_model_route.get("/bot/list")
@jwt_required
async def bot_listall(request: Request):
   try:
      
      user_payload = request.state.user
      user_id = user_payload.get("user_id")  # Assuming "user_id" is in the payload

      response = await query_get_all_bot_details(user_id)
      if len(response) == 0:
         raise Exception("No bot found.")
      
      logger.info(f"User ID: {user_id}, Api: bot_listall")
      return {"success": True,"message": None,"data": response}
   
   except ValueError as e:
      return {"success": False,"message": str(e),"data": None}
   except Exception as e:
      return {"success": False,"message": str(e),"data": None}
   


@gemini_model_route.put("/bot/update")
@jwt_required
async def bot_update(request: Request,bot: BOTUPDATEMODEL):
   try:
      
      user_payload = request.state.user
      user_id = user_payload.get("user_id")  # Assuming "user_id" is in the payload

      message = await update_bot_query(user_id=user_id,bot_id=bot.bot_id, bot_name=bot.bot_name,bot_category=bot.bot_category,bot_instruction=bot.bot_instruction)
      
      logger.info(f"User ID: {user_id}, Api: bot_update,  bot_id: {bot.bot_id}")
      return {"success": True,"message": None,"data": {"message": message,"bot_id": bot.bot_id, "user_id": user_id}}

   except Exception as e:
      return {"success": False,"message": str(e),"data": None}
   

@gemini_model_route.post("/bot/instruction-generate")
@jwt_required
async def instruction_generate_function(request: Request,bot: BOTCREATE):
   try:
      
      user_payload = request.state.user
      user_id = user_payload.get("user_id")
      
      response = await generate_bot_instruction(bot_name=bot.bot_name, bot_category=bot.bot_category)
      # print(response.text)
      logger.info(f"User ID: {user_id}, Api: instruction_generate_function,  bot_name: {bot.bot_name}")
      return {"success": True,"message": None,"data": {"bot_instruction": response}}

   except Exception as e:
      return {"success": False,"message": str(e),"data": None} 

@gemini_model_route.delete("/bot/delete")
@jwt_required
async def bot_delete(request: Request,bot: BOTUPDATEMODEL):
   try:
      
      user_payload = request.state.user
      user_id = user_payload.get("user_id")  # Assuming "user_id" is in the payload

      message = await delete_bot_query(user_id=user_id,bot_id=bot.bot_id)
      
      logger.info(f"User ID: {user_id}, Api: bot_delete,  bot_id: {bot.bot_id}")
      return {"success": True,"message": None,"data": {"message": message,"bot_id": bot.bot_id, "user_id": user_id}}

   except Exception as e:
      return {"success": False,"message": str(e),"data": None}