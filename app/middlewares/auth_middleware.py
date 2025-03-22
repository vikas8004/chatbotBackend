import jwt
from fastapi import HTTPException, Request
import os
from dotenv import load_dotenv
load_dotenv()
def verify_jwt(request:Request):
    access_token=request.cookies.get("access_token") or request.headers.get("Authorization")
    if not access_token:
        print("iside unauth")
        raise HTTPException(status_code=401, detail="Unauthorized")
    if access_token and access_token.startswith("Bearer "):
        access_token = access_token.split("Bearer ")[1]
    # print("access_token",access_token)
    try:
        decoded_data=jwt.decode(access_token,os.getenv("JWT_SECRET"),algorithms=["HS256"])
        # print(decoded_data)
        return decoded_data
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
     
    