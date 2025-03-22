from fastapi import APIRouter, Depends

from app.middlewares.auth_middleware import verify_jwt
from app.controllers.thread_controller import delete_found_thread, get_all_thread

thread_router=APIRouter()

# get all threads
@thread_router.get("/")
def all_threads(decoded_info:dict=Depends(verify_jwt)):
    return get_all_thread(decoded_info)

# delete thread
@thread_router.delete("/delete/{thread_id}")
def delete_thread(thread_id:str,decoded_info:dict=Depends(verify_jwt)):
    print(thread_id)
    return delete_found_thread(thread_id,decoded_info)