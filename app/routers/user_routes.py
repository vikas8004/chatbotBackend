from fastapi import APIRouter, Request, Response,status,Depends

from app.models.user_model import User
from app.controllers.user_controller import auto_login, signin, signup
from app.middlewares.auth_middleware import verify_jwt


user_router=APIRouter()
@user_router.post("/signup",status_code=status.HTTP_201_CREATED)
def signup_user(user:User):
    # print(user)
    return signup(user)

@user_router.post("/signin")
async def signin_user(user:Request,response:Response):
    return await signin(user,response)

# auto verify and login route
@user_router.get("/auto_login")
async def auto_verify_and_login(request:Request,decoded_user:dict=Depends(verify_jwt)):
    return auto_login(decoded_user,request.cookies.get("access_token"))

# user logout
@user_router.get("/logout")
async def logout(response:Response):
    response.delete_cookie("access_token")
    return {"message":"logged out successfully"}