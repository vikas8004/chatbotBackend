from fastapi import APIRouter, Depends,status
from app.controllers.chat_bot_controller import generate_response, get_all_messages, save_msg_to_db
from app.models.input_model import ContentRequest
from app.middlewares.auth_middleware import verify_jwt

chat_bot_router=APIRouter()

@chat_bot_router.post("/generate")
def generate_bot_response(request:ContentRequest,decoded_user:dict=Depends(verify_jwt)):
    return generate_response(request,decoded_user)

# get all messages
@chat_bot_router.get("/messages/{thread_id}")
def all_messages(thread_id:str,encoded_data:dict=Depends(verify_jwt)):
    print(thread_id)
    return get_all_messages(thread_id)