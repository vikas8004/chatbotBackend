from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from dotenv import load_dotenv
import os
load_dotenv()
# Initialize the Google Gemini client with your API key
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Create a FastAPI instance
app = FastAPI()
origins = [
    "http://localhost",  # Local development
    "http://localhost:5173",  # If your front end is running on port 3000
]
app.add_middleware(
     CORSMiddleware,
    allow_origins=origins,  # List of allowed origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Define the input model for the request
class ContentRequest(BaseModel):
    content: str

# Create a route to generate content using Gemini
@app.post("/generate")
async def generate_content(request: ContentRequest):
    # print(request)
    prompt=request.content
    
    try:
        # Generate content using the Gemini model
        response = client.models.generate_content(
            model="gemini-2.0-flash",  # Specify the model
            contents=prompt,  # The content you want to generate
        )

        # Return the generated text as a response
        return {"generated_text": response.text}
    except Exception as e:
        return {"error": str(e)}
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app",host="localhost",port=1200,reload=True)
    
