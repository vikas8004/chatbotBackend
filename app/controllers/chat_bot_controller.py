from fastapi.responses import StreamingResponse
from datetime import datetime
import os
import uuid
import google.generativeai as genai  # Correct import
from app.models.input_model import ContentRequest
from dotenv import load_dotenv
from app.database import db
from app.controllers.thread_controller import create_thread
from bson import ObjectId
from app.utils.conver_objectid_to_str import convert_objectid_to_str

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Initialize the Gemini model
model = genai.GenerativeModel("gemini-1.5-flash")  # ✅ Correct way to initialize

# Function to save messages to the database
def save_msg_to_db(msg_data: dict):
    msg_id = db.messages.insert_one(msg_data).inserted_id
    return str(msg_id)

# Function to generate responses using streaming
async def generate_response(request: ContentRequest, decoded_user):
    try:
        thread_id = request.thread_id
        found_thread = db.threads.find_one({"thread_id": thread_id})
        is_new_thread = not bool(found_thread)  # True if thread is new
        
        if is_new_thread:
            # Generate thread title using AI
            title_response = model.generate_content(f"Generate a short title in not greater than 5 words: {request.content}")
            title = title_response.text.strip() if title_response.text else f"{request.content[:20]}..."
            
            inserted_thread_id = create_thread({
                "thread_id": str(thread_id),
                "user_id": decoded_user["id"],
                "title": title,
                "created_at": datetime.utcnow(),
                "last_updated": datetime.utcnow(),
            })

        save_msg_to_db({
            "thread_id": str(thread_id),
            "role": "user",
            "content": request.content,
            "timestamp": datetime.utcnow()
        })

        # Streaming function
        async def response_generator():
            refined_prompt = (
    f"### 📝 **Response Formatting Guidelines**\n"
    f"- ✅ **Use bullet points** for key takeaways.\n"
    f"- 🔹 Highlight important terms using **bold text**.\n"
    f"- 📌 If explaining a concept, provide **concise yet detailed information**.\n"
    f"- 🎯 Ensure answers are **accurate, logical, and relevant** to the query.\n"
    f"- 🔥 Add relevant **examples, real-world applications, or comparisons**.\n\n"
    
    f"---\n"
    f"### 🔍 **Structural Enhancements for Better Clarity**\n"
    f"- 1️⃣ **Headings & Subheadings:** Organize content into sections.\n"
    f"- 2️⃣ **Numbered Lists:** Use when explaining steps or processes.\n"
    f"- 3️⃣ **Tables & Comparisons:** If applicable, structure data using tables.\n"
    f"- 4️⃣ **Examples & Use Cases:** Provide real-world applications where possible.\n"
    f"- 5️⃣ **Code Snippets:** Format properly for better readability.\n"
    f"- 6️⃣ **Do’s & Don’ts:** If explaining best practices, list them clearly.\n"
    f"- 7️⃣ **Recap & Summary:** End with key takeaways for quick review.\n"
    f"- 8️⃣ **Next Steps/Recommendations:** Suggest further actions when needed.\n"
    f"- 9️⃣ **Pros & Cons Analysis:** If relevant, provide advantages vs. disadvantages.\n"
    f"- 🔟 **Frequently Asked Questions (FAQs):** Address common doubts proactively.\n\n"

    f"---\n"
    f"### 💡 **Additional Enhancements for Engagement**\n"
    f"- 🎨 Use **emojis** for better visualization and readability.\n"
    f"- 🔗 If providing links, use markdown format like this:  \n"
    f"  - [🔵 Example Link](https://example.com)\n"
    f"- 🏆 Use **real-world analogies** to simplify complex ideas.\n"
    f"- 📊 **Diagrams, ASCII Art, or Tables** (if applicable) to explain technical concepts.\n"
    f"- ⚡ Use **short, impactful sentences** instead of lengthy paragraphs.\n"
    f"- ❗ Avoid **fluff**—keep responses precise and to the point.\n"
    f"- 🔄 If applicable, mention **related concepts** that help in understanding.\n\n"

    f"---\n"
    f"### 📌 **If There Are Instructions to Follow**\n"
    f"- **Provide clear step-by-step instructions.**\n"
    f"- **Use numbered lists (1️⃣, 2️⃣, 3️⃣, etc.)** for better guidance.\n"
    f"- **Include visuals** (ASCII diagrams, markdown images, or flowcharts) where possible.\n"
    f"- **Example:**\n\n"
    
    f"#### 🛠 **How to Install XYZ:**\n"
    f"1️⃣ **Download** the software from [🔵 here](https://example.com)\n"
    f"2️⃣ **Open the installer** and follow on-screen instructions.\n"
    f"3️⃣ **Verify installation** using:\n"
    f"   ```bash\n"
    f"   xyz --version\n"
    f"   ```\n"
    f"4️⃣ **Start using** XYZ by running:\n"
    f"   ```bash\n"
    f"   xyz start\n"
    f"   ```\n"
    f"✅ You are now ready to use XYZ!\n\n"

    f"---\n"
    f"### 🛠 **Best Practices & Common Mistakes**\n"
    f"- ✅ **Do This:**\n"
    f"  - Use structured formatting (headings, bullet points, etc.).\n"
    f"  - Provide real-world examples where possible.\n"
    f"  - Keep the response clear, logical, and factually accurate.\n\n"
    
    f"- ❌ **Avoid This:**\n"
    f"  - Overloading with unnecessary details.\n"
    f"  - Writing excessively long paragraphs without structure.\n"
    f"  - Missing key points related to the query.\n\n"

    f"---\n"
    f"### 💬 **User Query:**\n"
    f"{request.content}\n\n"
    f"### 🤖 **AI Response:**"
)

    
            response = model.generate_content(
                refined_prompt,
                stream=True  # ✅ Enable streaming
            )

            collected_text = ""  # Store full response for saving
            for chunk in response:
                if hasattr(chunk, "text") and chunk.text:
                    collected_text += chunk.text
                    # print(chunk.text)  # Print each chunk                
                    yield chunk.text  # Stream each chunk
            
            # Save response once streaming is complete
            if collected_text:
                save_msg_to_db({
                    "thread_id": str(thread_id),
                    "role": "assistant",
                    "content": collected_text,
                    "timestamp": datetime.utcnow()
                })

        return StreamingResponse(response_generator(), media_type="text/plain")

    except Exception as e:
        return {"error": str(e)}

# getting all messages
def get_all_messages(thread_id:str):
    
    all_messages=db.messages.find({"thread_id":thread_id})
    all_messages=[convert_objectid_to_str(message,"_id") for message in all_messages]
    return {"messages":all_messages}