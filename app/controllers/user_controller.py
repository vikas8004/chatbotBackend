import os
from bson import ObjectId
from app.models.user_model import User
from app.database import db
from fastapi import HTTPException, Response, status,Request
from dotenv import load_dotenv
from app.utils.bcrypt import hash_str, verify
from app.utils.jwt import create_jwt_token
from app.utils.conver_objectid_to_str import convert_objectid_to_str
load_dotenv()
def signup(user: User):
    try:
        # Convert user model to dictionary
        user = user.model_dump()

        # Check if the user already exists in the database
        found_user = db.users.find_one({"email": user["email"]})
        if found_user:
            raise HTTPException(status.HTTP_409_CONFLICT, detail={"msg": "User already exists.."})

        # Hash the password before storing it
        user["password"] = hash_str(user["password"])

        # Insert the user into the database
        inserted_id = db.users.insert_one(user).inserted_id
        return {"inserted_id": str(inserted_id)}

    except HTTPException as e:
        # Handle known HTTPException (like conflict)
        print(e)
        print(f"HTTP Exception occurred: {e.detail}")
        raise e  # Re-raise the HTTPException to propagate it

    except Exception as e:
        # Catch other unexpected errors (e.g., database errors)
        print(f"Unexpected error occurred: {e}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail={"msg": "Internal server error"})

# signning in the user 
async def signin(data:Request,response:Response):
    try:
        data=await data.json()
        # print(data)
        found_user=db.users.find_one({"email":data["email"]})
        # print(found_user)
        if not found_user:
            raise HTTPException(status.HTTP_404_NOT_FOUND,{"msg":"User not found.."})
        is_matched_password=verify(data["password"],found_user["password"])
        # print(is_matched_password)
        if not is_matched_password:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED,{"msg":"Invalid credentials"})
        token=create_jwt_token(str(found_user["_id"]))
        response.set_cookie(
            key="access_token",
            value=token,
            max_age=86400,  # 1 day
            samesite="Lax",  # Required for cross-site cookies
            secure=False if os.getenv("ENV") == "development" else True,  # Secure only in production
            httponly=True
        ) 
        found_user=convert_objectid_to_str(found_user,"_id")
        del found_user["password"]    
        found_user["access_token"]=token  
        return {"msg":"Logged in successfully","user":found_user}
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"inside sign in error {e}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR,{"Internal server error"})

# auto verify and login function
def auto_login(decoded_user,access_token):
    # print("hello auto login",decoded_user)
    found_user=db.users.find_one({"_id":ObjectId(decoded_user["id"])})
    found_user=convert_objectid_to_str(found_user,"_id")
    del found_user["password"]
    found_user["access_token"]=access_token
    # print(found_user)    
    return {"decoded_user":found_user}