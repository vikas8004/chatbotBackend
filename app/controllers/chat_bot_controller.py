from datetime import datetime
import os
import uuid
from google import genai
from app.models.input_model import ContentRequest
from dotenv import load_dotenv
from app.database import db
from app.controllers.thread_controller import create_thread
from bson import ObjectId

from app.utils.conver_objectid_to_str import convert_objectid_to_str
load_dotenv()
client=genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# saving the message to database
def save_msg_to_db(msg_data:ContentRequest):
    # print(msg_data)
    msg_id=db.messages.insert_one(msg_data).inserted_id
    return str(msg_id)
    
    
def generate_response(request: ContentRequest, decoded_user):
    try:
        thread_id = request.thread_id
        found_thread = db.threads.find_one({"thread_id": thread_id})
        
        is_new_thread = not bool(found_thread)  # True if thread is new
        
        if is_new_thread:
            # Generate thread title using AI
            title_response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=f"Generate a short title for this conversation without markdown content and in plain text: {request.content}"
            )
            title = title_response.text.strip() if title_response.text else f"{request.content[:20]}..."
            
            inserted_thread_id=create_thread({
                "thread_id": str(thread_id),
                "user_id": decoded_user["id"],
                "title": title,
                "created_at": datetime.utcnow(),
                "last_updated": datetime.utcnow(),
            })

        save_msg_to_db({
            "thread_id": str(thread_id),  # UUID reference to Thread
            "role": "user",
            "content": request.content,
            "timestamp": datetime.utcnow()
        })

        # Generate content using the Gemini model
        response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=f"""
    {request.content}

    ---
    ### **📝 Response Formatting Guidelines**
    - ✅ **Use bullet points** for key takeaways.  
    - 🔹 Highlight important terms using **bold text**.  
    - 📌 If explaining a concept, provide **concise yet detailed information**.  
    - 🎯 Ensure answers are **accurate, logical, and relevant** to the query.  

    ---
    ### **🔍 Structural Enhancements for Better Clarity**
    - 1️⃣ **Headings & Subheadings:** Organize content into sections.  
    - 2️⃣ **Numbered Lists:** Use when explaining steps or processes.  
    - 3️⃣ **Tables & Comparisons:** If applicable, structure data using tables.  
    - 4️⃣ **Examples & Use Cases:** Provide real-world applications where possible.  
    - 5️⃣ **Code Snippets:** Format properly for better readability.  
    - 6️⃣ **Do’s & Don’ts:** If explaining best practices, list them clearly.  
    - 7️⃣ **Recap & Summary:** End with key takeaways for quick review.  
    - 8️⃣ **Next Steps/Recommendations:** Suggest further actions when needed.  

    ---
    ### **💡 Additional Enhancements for Engagement**
    - 🎨 Use **emojis** for better visualization and readability.  
    - 🔗 If providing links, format them in **blue color** like this:  
      - **[Example Link](https://example.com)** 🔵  
    - 🏆 Use **real-world analogies** to simplify complex ideas.  
    - 📊 **Diagrams or ASCII Art** (if applicable) to explain technical concepts.  
    - ⚡ Use **short, impactful sentences** instead of lengthy paragraphs.  
    - ❗ Avoid **fluff**—keep responses precise and to the point.  

    ---
    ### **📌 If There Are Instructions to Follow**
    - **Provide clear step-by-step instructions.**  
    - **Use numbered lists (1️⃣, 2️⃣, 3️⃣, etc.)** for better guidance.  
    - **Include visuals** (ASCII diagrams, markdown images, or flowcharts) where possible.  
    - **Example:**  

      #### **How to Install XYZ:**  
      1️⃣ **Download** the software from [here](https://example.com) 🔵  
      2️⃣ **Open the installer** and follow on-screen instructions.  
      3️⃣ **Verify installation** using `xyz --version`.  
      4️⃣ **Start using** XYZ by running `xyz start`. ✅  

    ---
    """
)

        msg_id = None
        if response.text:
            msg_id = save_msg_to_db({
                "thread_id": str(thread_id),
                "role": "assistant",
                "content": response.text,
                "timestamp": datetime.utcnow()
            })
        
        if is_new_thread:
            return {
                "message": {
                    "thread_id": str(thread_id),
                    "role": "assistant",
                    "content": response.text,
                    "_id": msg_id
                },
                "thread": {
                    "thread_id": thread_id,
                    "title": title,
                    "created_at": datetime.utcnow(),
                    "last_updated": datetime.utcnow(),
                    "_id": inserted_thread_id
                }
            }
        return {
            "message": {
                "thread_id": str(thread_id),
                "role": "assistant",
                "content": response.text,
                "_id": msg_id
            },
            
        }
    except Exception as e:
        return {"error": str(e)}

# getting all messages
def get_all_messages(thread_id:str):
    
    all_messages=db.messages.find({"thread_id":thread_id})
    all_messages=[convert_objectid_to_str(message,"_id") for message in all_messages]
    return {"messages":all_messages}