import os
from dotenv import load_dotenv
load_dotenv()
from functools import wraps
import jwt
from fastapi import Request
from typing import Callable
from datetime import datetime, timedelta
from jwt import InvalidTokenError, ExpiredSignatureError

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
algorithm = os.getenv("algorithm")



def jwt_required(f: Callable):
    @wraps(f)
    async def decorated_function(request: Request, *args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            raise ValueError("Token is missing")
        
        token = token.replace("Bearer ", "")  # Remove "Bearer " if it's there
        
        try:
            # Decode the JWT token, automatically checking for expiry
            decoded_token = jwt.decode(token, JWT_SECRET_KEY, algorithm)
            request.state.user = decoded_token  # Store the decoded payload in request.state


        except Exception as e:
            # raise str(e)
            return {"success": False,"message": "Invalid JWT token " + str(e),"data": None}
        
        # Call the original function with all arguments (including chat and request)
        return await f(request, *args, **kwargs)

    return decorated_function





async def generate_jwt(user_id,user_name,user_email):
    try:

        payload = {
            "user_id": user_id,
            "name":user_name,
            "email":user_email,
            "exp": datetime.utcnow() + timedelta(days=1),  
            "role": "user"
        }
        token = jwt.encode(payload, JWT_SECRET_KEY, algorithm)
        return token

    except Exception as e:
        raise ValueError("An error occurred while generating JWT token: " + str(e))


# import jwt
# from datetime import datetime, timedelta

# JWT_SECRET_KEY = "4e2e0b70-cd8f-4bb9-ac5f-7a0778975ef7-9e4c791b-d525-48ff-9a81-dde919632936"
# algorithm = "HS256"

# def generate_jwt(user_id,user_name,user_email):
#     payload = {
#         "user_id": user_id,
#         "name":user_name,
#         "email":user_email,
#         "exp": datetime.utcnow() + timedelta(days=1),  
#         "role": "user"
#     }
#     token = jwt.encode(payload, JWT_SECRET_KEY, algorithm)
#     return token


# def decode_jwt(token):
#     data = jwt.decode(token, JWT_SECRET_KEY, algorithm)
#     print(data)

#     if data["user_id"]:
#         print("Successful")
#     else:
#         print("Wrong JWT token")
    
#     return data

# token = generate_jwt(1,"John Doe","b9ZsI@example.com")
# print(token)

# ans = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJuYW1lIjoiSm9obiBEb2UiLCJlbWFpbCI6ImI5WnNJQGV4YW1wbGUuY29tIiwiZXhwIjoxNzM4NTI1MDM1LCJyb2xlIjoidXNlciJ9.ImiJP-DAjeiprpb6NDjDsr_yUgUkBDCehX1yauVbZVI"

# decode_jwt(ans)
