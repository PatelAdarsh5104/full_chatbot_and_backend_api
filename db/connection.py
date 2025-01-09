import os
import aiomysql 
from aiomysql import create_pool
from dotenv import load_dotenv
load_dotenv()

async def init_db_pool():
        pool = await aiomysql.create_pool(
            host=os.getenv("MYSQL_ADDON_HOST"),
            user=os.getenv("MYSQL_ADDON_USER"),
            password=os.getenv("MYSQL_ADDON_PASSWORD"),
            db=os.getenv("MYSQL_ADDON_DB"),
        )
        return pool