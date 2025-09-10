import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai

# FastAPI app initialization

app = FastAPI(title="Health Chatbot Backend")

# Allow frontend requests (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  #Change it to your frontend URL if you have it rready
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# Load OpenAI API key
# -------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  #here we have to insert the security key that is paid
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

# -------------------------
# Request body structure
# -------------------------
class ChatRequest(BaseModel):
    message: str
    user_id: str = "guest"


# Health check endpoint

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


# Chat endpoint

@app.post("/chat")
async def chat(req: ChatRequest):
    if not openai.api_key:
        raise HTTPException(
            status_code=500,
            detail="OPENAI_API_KEY not configured. Set it as an environment variable."
        )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", 
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful, cautious health assistant. "
                        "Give general advice and always include a disclaimer: "
                        "You are not a doctor and users should consult a healthcare professional for diagnosis."
                    )
                },
                {"role": "user", "content": req.message}
            ],
            temperature=0.6,
            max_tokens=400,
        )

        reply = response["choices"][0]["message"]["content"].strip()
        return {"reply": reply}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
