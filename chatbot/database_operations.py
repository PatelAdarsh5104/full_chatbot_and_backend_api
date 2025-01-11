from aiomysql import create_pool 
from dotenv import load_dotenv
from db.connection import init_db_pool
import aiomysql
from datetime import datetime, timezone


async def insert_question_answer(user_id, session_id, question, answer):
    pool = await init_db_pool()
    try:
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                # Current UTC timestamp
                utc_now = datetime.now(timezone.utc)
                
                # SQL query to insert data
                insert_query = '''
                    INSERT INTO chatbot_chat_history (user_id, session_id, question, answer, created_at, updated_at) 
                    VALUES (%s, %s, %s, %s, %s, %s)
                '''
            
                # Execute the query
                await cursor.execute(insert_query, (user_id, session_id, question, answer, utc_now, utc_now))
                await conn.commit()

                return {"message": "Question and Answer inserted successfully."}
            
    except Exception as e:
        raise Exception(f"An error occurred while inserting data: {e}")

    finally:
        pool.close()
        await pool.wait_closed()
        print("Database pool closed.")            


async def get_chat_history_sql(user_id, session_id):
    pool = await init_db_pool()
    try:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                
                # Query to retrieve all records
                await cursor.execute("""SELECT * FROM chatbot_chat_history WHERE user_id=%s AND session_id=%s  AND EXISTS (
                        SELECT 1 FROM session WHERE user_id = %s AND session_id = %s AND active = 1)  """, 
                        (user_id, session_id,user_id, session_id))
                records = await cursor.fetchall()
            
                return records

    except Exception as e:
        raise Exception(f"An error occurred while retrieving chat history. {e}")

    finally:
        pool.close()
        await pool.wait_closed()
        print("Database pool closed.") 