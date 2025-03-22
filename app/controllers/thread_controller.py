import json
from bson import ObjectId
from app.models.input_model import Thread
from app.database import db
from app.utils.conver_objectid_to_str import convert_objectid_to_str
# get all thread
def get_all_thread(decoded_info: dict):
    # Fetch threads for the specific user
    threads_cursor = db.threads.find({"user_id": ObjectId(decoded_info["id"])})

    # Ensure unique threads based on 'thread_id' and convert ObjectId fields
    unique_threads = {
        str(thread["thread_id"]): convert_objectid_to_str(thread, "user_id", "_id")
        for thread in threads_cursor
    }.values()

    return {"threads": list(unique_threads)}

# creating thread
def create_thread(thread_data:Thread):
    thread_data=thread_data
    thread_data["user_id"]=ObjectId(thread_data["user_id"])
    # print(thread_data)
    inserted_thread_id=db.threads.insert_one(thread_data).inserted_id
    return str(inserted_thread_id)
    
# delete thread
def delete_found_thread(thread_id:str,decoded_info:dict):
    # print(thread_id)
    db.threads.delete_many({"thread_id":thread_id,"user_id":ObjectId(decoded_info["id"])})
    db.messages.delete_many({"thread_id":thread_id})
    return {"message":"Chat deleted successfully"}
    
    