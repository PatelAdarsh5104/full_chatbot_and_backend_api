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
                print("User signup and Data inserted successfully.")
                return {"message": "user sign in successfully.", "user_id": user_id}

    except Exception as e:
        raise Exception(f"An error occurred while inserting data: {e}")

    finally:
        pool.close()
        await pool.wait_closed()
        print("Database pool closed.")