from fastapi import HTTPException
from fastapi import APIRouter
from typing import Annotated
from fastapi import Depends
from assistant.models import Message, MemoryFact, Conversation
from sqlalchemy.orm import Session
from pydantic import BaseModel
from assistant.database import get_db
from assistant.routers.auth import get_current_user
from assistant.ai import get_ai_response, get_memory_facts
import json

chat_router = APIRouter()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]



class ChatRequest(BaseModel):
    content: str
    conversation_id: int





@chat_router.post("/chat")
async def create_chat(user: user_dependency, db: db_dependency, request: ChatRequest):
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    conversation = db.query(Conversation).filter(Conversation.id == request.conversation_id).first()
    if conversation is None or conversation.user_id != user.get("user_id"):
        raise HTTPException(status_code=403, detail="Wrong Conversation")

    user_message = Message(role="user",
                           content=request.content,
                           conversation_id=request.conversation_id)

    db.add(user_message)
    db.commit()

    history = db.query(Message).filter(Message.conversation_id == user_message.conversation_id).all()
    memory_facts = get_memory_facts(history)
    try:
        facts = json.loads(memory_facts)
        for fact in facts:
            memory_fact = MemoryFact(
                key=fact["key"],
                value=fact["value"],
                user_id=user.get("user_id")
            )
            db.add(memory_fact)
        db.commit()

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid memory facts JSON")

    all_memory_facts = db.query(MemoryFact).filter(MemoryFact.user_id == user.get("user_id")).all()



    ai_reply = get_ai_response(user_message.content, history, all_memory_facts)

    ai_message = Message(
        role="assistant",
        content=ai_reply,
        conversation_id=request.conversation_id
    )
    db.add(ai_message)
    db.commit()

    return {"ai_reply" : ai_message.content}




