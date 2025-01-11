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


async def create_table_session():
    pool = await init_db_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute('''CREATE TABLE IF NOT EXISTS session (
                                        id INT AUTO_INCREMENT PRIMARY KEY,
                                        user_id VARCHAR(255) NOT NULL,
                                        session_id VARCHAR(255) NOT NULL,
                                        active TINYINT(1),
                                        created_at DATETIME,
                                        updated_at DATETIME)''')
            await conn.commit()
            print(f"Table chatbot_chat_history created successfully in {os.getenv('MYSQL_ADDON_DB')} database.")

async def create_table_userdetails():
    pool = await init_db_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute('''CREATE TABLE IF NOT EXISTS userdetails (
                                        id INT AUTO_INCREMENT PRIMARY KEY,
                                        user_id VARCHAR(36) NOT NULL,
                                        user_name VARCHAR(45) NOT NULL,
                                        user_email VARCHAR(100) DEFAULT NULL,
                                        user_password VARCHAR(100) DEFAULT NULL,
                                        user_phone VARCHAR(13) DEFAULT NULL,
                                        created_at DATETIME DEFAULT NULL
                                        )   ''')
            
            await conn.commit()
            print(f"Table chatbot_chat_history created successfully in {os.getenv('MYSQL_ADDON_DB')} database.")


# asyncio.run(create_table_chatbot())
# asyncio.run(create_table_session())
# asyncio.run(create_table_userdetails())