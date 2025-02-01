from aiomysql import create_pool 
import bcrypt
from dotenv import load_dotenv
from db.connection import init_db_pool
import aiomysql
from datetime import datetime, timezone
import uuid
from user.send_otp import send_otp


### Get all user details function optimized
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



### Login User function optimized
async def login_and_manage_session(user_name, password):
    pool = await init_db_pool()
    try:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                # Fetch user details in one query
                select_query = '''
                    SELECT user_password, user_id, user_name, user_email
                    FROM userdetails
                    WHERE user_name = %s
                '''
                await cursor.execute(select_query, (user_name,))
                user_record = await cursor.fetchone()

                # If user does not exist, raise an error
                if not user_record:
                    raise Exception("User does not exist, please sign up.")

                # Check the password
                if not bcrypt.checkpw(password.encode('utf-8'), user_record["user_password"].encode('utf-8')):
                    raise Exception("Invalid username or password.")

                # Generate new session in the same transaction
                utc_now = datetime.now(timezone.utc)
                session_id = str(uuid.uuid4())

                # Inactivate any previous active session for the user
                deactivate_session_query = '''
                    UPDATE session 
                    SET active = 0, updated_at = %s 
                    WHERE user_id = %s AND active = 1
                '''
                await cursor.execute(deactivate_session_query, (utc_now, user_record["user_id"]))

                # Insert new session
                insert_session_query = '''
                    INSERT INTO session (user_id, session_id, active, created_at)
                    VALUES (%s, %s, %s, %s)
                '''
                await cursor.execute(insert_session_query, (user_record["user_id"], session_id, 1, utc_now))

                # Commit the transaction
                await conn.commit()

                # Return login details with session info
                return {
                        "response": "Login successful!",
                        "user_id": user_record["user_id"],
                        "session_id": session_id,
                        "user_name": user_record["user_name"],
                        "user_email": user_record["user_email"]
                    }

    except Exception as e:
        raise Exception(f"Login error: {e}")
    
    finally:
        pool.close()
        await pool.wait_closed()
        print("Database pool closed.")


#### Optimized code for dublicate_user function
# async def dublicate_user(user_name):
#     pool = await init_db_pool()
#     try:
#         async with pool.acquire() as conn:
#             async with conn.cursor() as cursor:
#                 query = 'SELECT COUNT(*) FROM userdetails WHERE user_name = %s'
#                 await cursor.execute(query, (user_name,))
#                 count = await cursor.fetchone()
#                 return count[0] > 0  # Return True if record exists
            
#     except Exception as e:
#         raise Exception(f"Error checking for duplicate user: {e}")

#     finally:
#         pool.close()
#         await pool.wait_closed()
#         print("Database pool closed.")


### Optimizes code for signup_user and Duplicate user and sessionid_generate functions 
async def signup_user(user_name, user_email, user_password, user_phone, name):
    pool = await init_db_pool()
    try:
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                # Start a single transaction
                await conn.begin()

                # Check for duplicate user_name
                query = 'SELECT COUNT(*) FROM userdetails WHERE user_name = %s'
                await cursor.execute(query, (user_name,))
                count = await cursor.fetchone()
                # return count[0] > 0  # Return True if record exists
                if count[0] > 0:
                    raise Exception("User already exists with this name. Try a different User_name.")

                # Insert user details
                utc_now = datetime.now(timezone.utc)
                user_id = str(uuid.uuid4())
                
                # Hash password once
                hashed_password = bcrypt.hashpw(user_password.encode('utf-8'), bcrypt.gensalt())

                insert_user_query = '''
                    INSERT INTO userdetails (user_id, user_name, name, user_email, user_password, user_phone, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                '''
                await cursor.execute(insert_user_query, (user_id, user_name, name, user_email, hashed_password, user_phone, utc_now))

                # Insert new session
                session_id = str(uuid.uuid4())
                insert_session_query = '''
                    INSERT INTO session (user_id, session_id, active, created_at)
                    VALUES (%s, %s, %s, %s)
                '''
                await cursor.execute(insert_session_query, (user_id, session_id, 1, utc_now))

                # Commit the transaction
                await conn.commit()

                return {"response": "User signed in successfully.", "user_id": user_id, "user_name": user_name, "session_id": session_id, "name": name}
    
    except Exception as e:
        raise Exception(f"Signin error: {e}")

    finally:
        pool.close()
        await pool.wait_closed()
        print("Database pool closed.")


### Logout function 
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
    

async def signup_user_email(user_name, user_email, user_phone, name):
    pool = await init_db_pool()
    try:
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                # Start a single transaction
                await conn.begin()

                # Check for duplicate user_name
                query = 'SELECT COUNT(*) FROM userdetails WHERE user_name = %s'
                await cursor.execute(query, (user_name,))
                count = await cursor.fetchone()
                # return count[0] > 0  # Return True if record exists
                if count[0] > 0:
                    raise Exception("User already exists with this name. Try a different User_name.")

                ## Generate & Send OTP
                otp = await send_otp(user_email)

                # Insert user details
                utc_now = datetime.now(timezone.utc)
                user_id = str(uuid.uuid4())
                
                insert_user_query = '''
                    INSERT INTO userdetails (user_id, user_name, name, user_email, otp, user_phone, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                '''
                await cursor.execute(insert_user_query, (user_id, user_name, name, user_email, otp, user_phone, utc_now))

                # Insert new session
                session_id = str(uuid.uuid4())
                insert_session_query = '''
                    INSERT INTO session (user_id, session_id, active, created_at)
                    VALUES (%s, %s, %s, %s)
                '''
                await cursor.execute(insert_session_query, (user_id, session_id, 1, utc_now))

                # Commit the transaction
                await conn.commit()

                return {"response": "User signed in successfully.", "user_id": user_id, "user_name": user_name, "session_id": session_id, "name": name}
    
    except Exception as e:
        raise Exception(f"Signin error: {e}")

    finally:
        pool.close()
        await pool.wait_closed()
        print("Database pool closed.")
