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
                                        user_id VARCHAR(255) NOT NULL,
                                        session_id VARCHAR(255) NOT NULL,
                                        bot_id VARCHAR(255) NOT NULL,
                                        question TEXT NOT NULL,
                                        answer TEXT NOT NULL,
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
                                        session_id VARCHAR(255) NOT NULL UNIQUE,
                                        active TINYINT(1),
                                        created_at DATETIME,
                                        updated_at DATETIME)''')
            await conn.commit()
            print(f"Table session created successfully in {os.getenv('MYSQL_ADDON_DB')} database.")

async def create_table_userdetails():
    pool = await init_db_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute('''CREATE TABLE IF NOT EXISTS userdetails (
                                        id INT AUTO_INCREMENT PRIMARY KEY,
                                        user_id VARCHAR(255) NOT NULL UNIQUE,
                                        user_name VARCHAR(255) NOT NULL UNIQUE,
                                        name VARCHAR(255) NOT NULL,
                                        user_email VARCHAR(255) NOT NULL UNIQUE,
                                        user_password VARCHAR(255) DEFAULT NULL,
                                        otp INT(10) DEFAULT NULL,
                                        user_phone VARCHAR(15) DEFAULT NULL,
                                        created_at DATETIME DEFAULT NULL
                                        )   ''')
            
            await conn.commit()
            print(f"Table userdetails created successfully in {os.getenv('MYSQL_ADDON_DB')} database.")


async def create_table_botsdetails():
    pool = await init_db_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute('''CREATE TABLE IF NOT EXISTS botsdetails (
                                        id INT AUTO_INCREMENT PRIMARY KEY,
                                        bot_id VARCHAR(255) UNIQUE NOT NULL,
                                        user_id VARCHAR(255) NOT NULL,
                                        name VARCHAR(255) NOT NULL,
                                        category VARCHAR(255) NOT NULL,
                                        instruction TEXT NOT NULL,
                                        isactive TINYINT(1),
                                        created_at DATETIME,
                                        updated_at DATETIME
                                        )   ''')
            
            await conn.commit()
            print(f"Table botsdetails created successfully in {os.getenv('MYSQL_ADDON_DB')} database.")



# asyncio.run(create_table_chatbot())
# asyncio.run(create_table_session())
# asyncio.run(create_table_userdetails())
# asyncio.run(create_table_botsdetails())