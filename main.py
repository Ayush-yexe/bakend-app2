import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai

app = FastAPI(title="Health Chatbot Backend")

# Allow cross-origin requests (so frontend can talk to backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load OpenAI key from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

# Define request body format
class ChatRequest(BaseModel):
    message: str
    user_id: str = "guest"

@app.get("/healthz")
async def healthz():
    """Health check endpoint"""
    return {"status": "ok"}

@app.post("/chat")
async def chat(req: ChatRequest):
    """Main chatbot endpoint"""
    if not openai.api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured in environment.")

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # or "gpt-4" if available
            messages=[
                {"role": "system", "content":
                 "You are a helpful health assistant. "
                 "Provide general advice, first-aid tips, and preventive care info. "
                 "Always include a disclaimer: you are not a doctor, and users must consult a healthcare professional."},
                {"role": "user", "content": req.message}
            ],
            temperature=0.6,
            max_tokens=400,
        )
        reply = response["choices"][0]["message"]["content"].strip()
        return {"reply": reply}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
