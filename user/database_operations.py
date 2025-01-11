from aiomysql import create_pool 
from dotenv import load_dotenv
from db.connection import init_db_pool
import aiomysql
from datetime import datetime, timezone
import uuid


# Async function to retrieve all records from the userdetails table
async def query_get_all_user_details():
    pool = await init_db_pool()
    try:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                # Query to retrieve all records
                await cursor.execute('SELECT * FROM userdetails')
                records = await cursor.fetchall()

                return records

    except Exception as e:
        raise Exception(f"An error occurred while retrieving data: {e}")

    finally:
        pool.close()
        await pool.wait_closed()
        print("Database pool closed.")




async def signup_user(user_name, user_email, user_password, user_phone):
    pool = await init_db_pool()
    try:
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                # Current UTC timestamp
                utc_now = datetime.now(timezone.utc)
                user_id = str(uuid.uuid4())
                # SQL query to insert data
                insert_query = '''
                    INSERT INTO userdetails (user_id, user_name, user_email, user_password, user_phone, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                '''
            
                # Execute the query
                await cursor.execute(insert_query, (user_id, user_name, user_email, user_password, user_phone, utc_now))
                await conn.commit()

                session_id = await sessionid_generate(user_id)

                return {"response": "user sign in successfully.", "user_id": user_id, "user_name": user_name, "session_id": session_id}

    except Exception as e:
        raise Exception(f"An error occurred while inserting data: {e}")

    finally:
        pool.close()
        await pool.wait_closed()
        print("Database pool closed.")


async def login_user(user_name):
    pool = await init_db_pool()
    try:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                
                # Fetch the hashed password from the database
                select_query = 'SELECT user_password, user_id, user_name,user_email FROM userdetails WHERE user_name = %s'
                await cursor.execute(select_query, (user_name,))
                record = await cursor.fetchone()

                # If no record is found, raise an error
                if not record:
                    raise Exception("User does not exist, please sign up.")
                
                return record


    except Exception as e:
        raise Exception(f"{e}")

    finally:
        pool.close()
        await pool.wait_closed()
        print("Database pool closed.")


async def dublicate_user(user_name):
    pool = await init_db_pool()
    try:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                
                # Fetch the hashed password from the database
                select_query = 'SELECT * FROM userdetails WHERE user_name = %s'
                await cursor.execute(select_query, (user_name,))
                record = await cursor.fetchone()
                return record

    except Exception as e:
        raise Exception(f"An error occurred while retrieving data: {e}")

    finally:
        pool.close()
        await pool.wait_closed()
        print("Database pool closed.")


async def sessionid_generate(user_id):
    pool = await init_db_pool()
    try:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                utc_now = datetime.now(timezone.utc)

                # Inactivate any previous active session for the user
                try:
                    inactive_query = """UPDATE session 
                    SET active = 0,
                    updated_at = %s 
                    WHERE user_id = %s AND active = 1"""
                    await cursor.execute(inactive_query, (utc_now,user_id,))
                    await conn.commit()

                except Exception as e:
                    raise Exception(f"An error occurred while inactivating previous session: {e}")

                ## Generate new session id
                session_id = str(uuid.uuid4())
                
                select_query = """ INSERT INTO session (user_id, session_id, active, created_at)
                    VALUES (%s, %s, %s, %s)"""
                await cursor.execute(select_query, (user_id,session_id,1,utc_now))
                await conn.commit() 
                
                return session_id
            
    except Exception as e:
        raise Exception(f"An error occurred while generating new session: {e}")

    finally:
        pool.close()
        await pool.wait_closed()
        print("Database pool closed.")


async def logout_session(user_id):
    pool = await init_db_pool()
    try:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                
                utc_now = datetime.now(timezone.utc)
                inactive_query = """UPDATE session 
                SET active = 0,
                updated_at = %s 
                WHERE user_id = %s AND active = 1"""
                await cursor.execute(inactive_query, (utc_now,user_id,))
                await conn.commit()

                return {"message": "Logout successful!", "user_id": user_id}

    except Exception as e:
        raise Exception(f"An error occurred while logging out: {e}")