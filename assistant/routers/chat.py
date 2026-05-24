from fastapi import HTTPException
from fastapi import APIRouter
from typing import Annotated
from fastapi import Depends
from assistant.models import Message
from sqlalchemy.orm import Session
from pydantic import BaseModel
from assistant.database import get_db
from assistant.routers.auth import get_current_user

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
    user_message = Message(role="user",
                           content=request.content,
                           conversation_id=request.conversation_id)

    db.add(user_message)
    db.commit()

    history = db.query(Message).filter(Message.conversation_id == user_message.conversation_id).all()

    ai_message = Message(role="assistant",
                         content="fake reply for now",
                         conversation_id=request.conversation_id)

    db.add(ai_message)
    db.commit()

    return {"ai_reply" : ai_message.content}




