from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.chat_bot_routes import chat_bot_router
from app.routers.user_routes import user_router
from app.routers.thread_routes import thread_router

# Create a FastAPI instance
app = FastAPI()
origins = [
    "http://localhost",  # Local development
    "http://localhost:5173",  # If your front end is running on port 5173
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # List of allowed origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)

app.include_router(chat_bot_router)  
app.include_router(user_router,prefix="/user") 
app.include_router(thread_router,prefix="/threads")
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app",host="localhost",port=1200,reload=True)
    
