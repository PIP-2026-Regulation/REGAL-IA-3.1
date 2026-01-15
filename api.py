"""FastAPI backend for EU AI Act Compliance Advisor."""

import os
import logging
from typing import List, Dict
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from src.legal_advisor import LegalAdvisor

load_dotenv(override=True)
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="EU AI Act Compliance Advisor API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite & CRA default ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state - session management
sessions: Dict[str, Dict] = {}


class Message(BaseModel):
    """User message model."""
    content: str
    session_id: str = "default"


class ChatResponse(BaseModel):
    """Chat response model."""
    message: str
    is_done: bool = False
    progress: Dict = {}


class SessionResponse(BaseModel):
    """Session info response."""
    session_id: str
    initial_prompt: str
    message: str


def get_initial_prompt():
    """Get the initial prompt for users."""
    return """Please describe your AI system in detail. Include:
- Primary purpose and functionality
- Technical approach (ML model type, algorithms)
- Data processed (types, sources, sensitivity)
- Deployment context (where, when, who uses it)
- Decision-making role (automated, human-in-loop)
- Potential impact on individuals

Be specific to enable accurate risk classification."""


def get_or_create_session(session_id: str) -> Dict:
    """Get or create a session."""
    if session_id not in sessions:
        try:
            advisor = LegalAdvisor()
            sessions[session_id] = {
                "advisor": advisor,
                "current_question": "",
                "awaiting_confirmation": False,
                "chat_history": []
            }
            logger.info(f"Created new session: {session_id}")
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            raise HTTPException(status_code=500, detail=f"Initialization failed: {e}")
    return sessions[session_id]


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "EU AI Act Compliance Advisor API",
        "version": "1.0.0",
        "endpoints": ["/chat", "/session/new", "/session/{session_id}/reset", "/health"]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "sessions_count": len(sessions)}


@app.post("/session/new", response_model=SessionResponse)
async def create_session():
    """Create a new session."""
    import uuid
    session_id = str(uuid.uuid4())
    get_or_create_session(session_id)

    return SessionResponse(
        session_id=session_id,
        initial_prompt=get_initial_prompt(),
        message="Session created successfully. Please describe your AI system."
    )


@app.post("/session/{session_id}/reset")
async def reset_session(session_id: str):
    """Reset a session."""
    session = get_or_create_session(session_id)
    session["advisor"].reset()
    session["current_question"] = ""
    session["awaiting_confirmation"] = False
    session["chat_history"] = []

    return {
        "message": "Session reset successfully",
        "initial_prompt": get_initial_prompt()
    }


@app.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a session."""
    if session_id in sessions:
        del sessions[session_id]
        return {"message": "Session deleted successfully"}
    raise HTTPException(status_code=404, detail="Session not found")


@app.post("/chat", response_model=ChatResponse)
async def chat(message: Message):
    """Process chat message."""
    if not message.content.strip():
        raise HTTPException(status_code=400, detail="Message content cannot be empty")

    session = get_or_create_session(message.session_id)
    advisor = session["advisor"]
    current_question = session["current_question"]
    awaiting_confirmation = session["awaiting_confirmation"]

    # Handle reset command
    if message.content.lower() == 'reset':
        advisor.reset()
        session["current_question"] = ""
        session["awaiting_confirmation"] = False
        session["chat_history"] = []
        return ChatResponse(
            message=f"🔄 System reset.\n\n{get_initial_prompt()}",
            is_done=False,
            progress=advisor.get_progress()
        )

    # Handle prohibited confirmation
    if awaiting_confirmation:
        if message.content.lower() in ['yes', 'y']:
            session["awaiting_confirmation"] = False
            next_q, is_done = advisor.ask_next_question()
            progress = advisor.get_progress()

            if is_done:
                response_msg = f"📊 **FINAL ASSESSMENT**\n\n{next_q}"
            else:
                session["current_question"] = next_q
                response_msg = f"[Q{progress['questions_asked']+1}/{progress['max_questions']}]\n\n{next_q}"

            return ChatResponse(
                message=response_msg,
                is_done=is_done,
                progress=progress
            )
        elif message.content.lower() in ['no', 'n']:
            # Generate final prohibited report
            session["awaiting_confirmation"] = False
            final_report = advisor.generate_prohibited_final_report()
            advisor.reset()
            return ChatResponse(
                message=f"📊 **FINAL ASSESSMENT - PROHIBITED SYSTEM**\n\n{final_report}",
                is_done=True,
                progress=advisor.get_progress()
            )
        else:
            session["awaiting_confirmation"] = False
            advisor.reset()
            return ChatResponse(
                message="⚠️ Assessment cancelled. Type your system description to start again.",
                is_done=False,
                progress=advisor.get_progress()
            )

    # Initial description
    if not advisor.model_description:
        response, is_prohibited = advisor.process_initial_description(message.content)

        if is_prohibited:
            session["awaiting_confirmation"] = True
            return ChatResponse(
                message=response,
                is_done=False,
                progress=advisor.get_progress()
            )

        advisor.model_description = message.content
        next_q, is_done = advisor.ask_next_question()
        progress = advisor.get_progress()

        if is_done:
            response_msg = f"📊 **FINAL ASSESSMENT**\n\n{next_q}"
        else:
            session["current_question"] = next_q
            response_msg = f"✅ Description received.\n\n[Q{progress['questions_asked']+1}/{progress['max_questions']}] {next_q}"

        return ChatResponse(
            message=response_msg,
            is_done=is_done,
            progress=progress
        )

    # Process answer
    try:
        next_q, is_done = advisor.process_answer(message.content, current_question)
        progress = advisor.get_progress()

        if is_done:
            response_msg = f"📊 **FINAL COMPLIANCE ASSESSMENT**\n\n{next_q}\n\n---\nType 'reset' to start a new assessment."
        else:
            session["current_question"] = next_q
            emoji = "🎯" if progress['questions_asked'] >= progress['min_questions'] else ""
            response_msg = f"[Q{progress['questions_asked']+1}/{progress['max_questions']}]{emoji}\n\n{next_q}"

        return ChatResponse(
            message=response_msg,
            is_done=is_done,
            progress=progress
        )
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {e}")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
