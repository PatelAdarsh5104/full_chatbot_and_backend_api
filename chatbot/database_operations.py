import uuid
from aiomysql import create_pool 
from dotenv import load_dotenv
from db.connection import init_db_pool
import aiomysql
from datetime import datetime, timezone


async def insert_question_answer(user_id, session_id, bot_id, question, answer):
    pool = await init_db_pool()
    try:
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                # Current UTC timestamp
                utc_now = datetime.now(timezone.utc)
                
                # SQL query to insert data
                insert_query = '''
                    INSERT INTO chatbot_chat_history (user_id, session_id, bot_id, question, answer, created_at, updated_at) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                '''
                print(bot_id)
                # Execute the query
                await cursor.execute(insert_query, (user_id, session_id, bot_id, question, answer, utc_now, utc_now))
                await conn.commit()

                return {"message": "Question and Answer inserted successfully."}
            
    except Exception as e:
        raise Exception(f"An error occurred while inserting data: {e}")

    finally:
        pool.close()
        await pool.wait_closed()
        print("Database pool closed.")            


async def create_bot(user_id, bot_name, bot_category, bot_instruction):
    pool = await init_db_pool()
    try:
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                # Current UTC timestamp
                utc_now = datetime.now(timezone.utc)
                
                # This will deactivate the old bot
                deactivate_oldbot = '''
                    UPDATE botsdetails 
                    SET isactive = 0, updated_at = %s 
                    WHERE user_id = %s AND isactive = 1
                '''
                await cursor.execute(deactivate_oldbot, (utc_now, user_id))



                isactive = 1
                bot_id = str(uuid.uuid4())
                # SQL query to insert data
                insert_query = '''
                    INSERT INTO botsdetails (user_id, bot_id, name, category, instruction, isactive, created_at) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                '''
            
                # Execute the query
                await cursor.execute(insert_query, (user_id, bot_id, bot_name, bot_category, bot_instruction, isactive, utc_now))
                await conn.commit()

                return bot_id
            
    except Exception as e:
        raise Exception(f"An error occurred while creating/inserting bot: {e}")

    finally:
        pool.close()
        await pool.wait_closed()
        print("Database pool closed.")            


async def query_get_all_bot_details(user_id):
    pool = await init_db_pool()
    try:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                # SQL query to retrieve all records
                await cursor.execute("SELECT * FROM botsdetails WHERE user_id=%s", (user_id))
                records = await cursor.fetchall()
                return records

    except Exception as e:
        raise Exception(f"An error occurred while retrieving bot details: {e}")

    finally:
        pool.close()
        await pool.wait_closed()
        print("Database pool closed.")


async def update_bot_query(user_id, bot_id, bot_name, bot_category, bot_instruction):
    pool = await init_db_pool()
    try:
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                # SQL query to retrieve all records
                utc_now = datetime.now(timezone.utc)

                updates = []
                values = []

                if bot_name is not None:
                    updates.append("name=%s")
                    values.append(bot_name)

                if bot_category is not None:
                    updates.append("category=%s")
                    values.append(bot_category)

                if bot_instruction is not None:
                    updates.append("instruction=%s")
                    values.append(bot_instruction)

                # SQL query to update data
                values.append(utc_now)
                values.append(user_id)
                values.append(bot_id)

                query = f"UPDATE botsdetails SET {', '.join(updates)}, updated_at=%s WHERE user_id=%s AND bot_id=%s"
                # print(query, tuple(values))
                await cursor.execute(query, tuple(values))
                await conn.commit()
                
                return "Bot updated successfully."
            
    except Exception as e:
        raise Exception(f"An error occurred while retrieving bot details: {e}")

    finally:
        pool.close()
        await pool.wait_closed()
        print("Database pool closed.")


async def delete_bot_query(user_id, bot_id):
    pool = await init_db_pool()
    try:
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                # SQL query to delete data
                await cursor.execute("DELETE FROM botsdetails WHERE user_id=%s AND bot_id=%s", (user_id, bot_id))
                await conn.commit()
                await cursor.execute("DELETE FROM chatbot_chat_history WHERE user_id=%s AND bot_id=%s", (user_id, bot_id))
                await conn.commit()
                
                return "Bot deleted successfully."
            
    except Exception as e:
        raise Exception(f"An error occurred while deleting bot: {e}")

    finally:
        pool.close()
        await pool.wait_closed()
        print("Database pool closed.")

async def get_chat_history_sql(user_id, bot_id):
    pool = await init_db_pool()
    try:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                
                await cursor.execute("""SELECT * FROM chatbot_chat_history WHERE user_id=%s AND bot_id=%s """, 
                        (user_id, bot_id))
                records = await cursor.fetchall()
            
                return records

    except Exception as e:
        raise Exception(f"An error occurred while retrieving chat history. {e}")

    finally:
        pool.close()
        await pool.wait_closed()
        print("Database pool closed.") 