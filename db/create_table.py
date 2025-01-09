import os
import asyncio
import aiomysql  
from dotenv import load_dotenv
load_dotenv()
from aiomysql import create_pool 
from connection import init_db_pool


async def create_table_chatbot():
    pool = await init_db_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute('''CREATE TABLE IF NOT EXISTS chatbot_chat_history (
                                        id INT AUTO_INCREMENT PRIMARY KEY,
                                        user_id VARCHAR(255),
                                        session_id VARCHAR(255),
                                        question TEXT,
                                        answer TEXT,
                                        created_at DATETIME,
                                        updated_at DATETIME)''')
            await conn.commit()
            print(f"Table chatbot_chat_history created successfully in {os.getenv('MYSQL_ADDON_DB')} database.")







# asyncio.run(create_table_chatbot())