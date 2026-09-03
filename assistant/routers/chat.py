from fastapi import APIRouter, HTTPException, status
from typing import Annotated
from fastapi import Depends
from redis.multidb import exception

from assistant.models import Message, MemoryFact, Conversation, DocumentEmbedding
from sqlalchemy.orm import Session
from pydantic import BaseModel
from assistant.database import get_db
from assistant.routers.auth import get_current_user
from assistant.ai import get_ai_response, get_memory_facts, get_vector
import json

chat_router = APIRouter()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]



class ChatRequest(BaseModel):
    content: str
    conversation_id: int


def process_background_chores(user_message: str, ai_message_content: str, conversation_id: int, user, db: Session, history: list):
    try:
        message_vector = get_vector(user_message)
        new_memory = DocumentEmbedding(
            content = user_message,
            embedding = message_vector
        )
        db.add(new_memory)

        ai_message = Message(
            role = "assistant",
            content = ai_message_content,
            conversation_id = conversation_id
        )
        db.add(ai_message)

        memory_facts = get_memory_facts(history)
        facts = json.loads(memory_facts)
        for fact in facts:
            key = fact.get('key') or list(fact.keys())[0]
            value = fact.get('value') or list(fact.values())[0]

            existing = db.query(MemoryFact).filter(MemoryFact.user_id == user.get("user_id"),
                                                   MemoryFact.key == key).first()
            if not existing:
                memory_fact = MemoryFact(
                    key = key,
                    value = value,
                    user_id = user.get("user_id")
                )
                db.add(memory_fact)
    except exception as e:
        print(f"Background task failed: {e}")
        db.rollback()

@chat_router.post("/chat", status_code=status.HTTP_201_CREATED)
async def create_chat(user: user_dependency, db: db_dependency, request: ChatRequest):
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    conversation = db.query(Conversation).filter(Conversation.id == request.conversation_id).first()
    if conversation is None or conversation.user_id != user.get("user_id"):
        raise HTTPException(status_code=403, detail="Wrong Conversation")

    user_message = Message(role="user",
                           content=request.content,
                           conversation_id=request.conversation_id)


    history = (db.query(Message).filter(Message.conversation_id == user_message.conversation_id)
               .order_by(Message.id.desc()).limit(5).all())
    history.reverse()
    memory_facts = get_memory_facts(history)

    print(memory_facts)
    try:
        facts = json.loads(memory_facts)
        for fact in facts:
            if 'key' in fact and 'value' in fact:
                key = fact['key']
                value = fact['value']
            else:
                key = list(fact.keys())[0]
                value = list(fact.values())[0]
            memory_fact = MemoryFact(
                key=key,
                value=value,
                user_id=user.get("user_id")
            )
            existing = db.query(MemoryFact).filter(MemoryFact.user_id==user.get("user_id"),
                                                   MemoryFact.key == key).first()
            if not existing:
                db.add(memory_fact)
        db.commit()

    except Exception as e:
        print(e)

    all_memory_facts = db.query(MemoryFact).filter(MemoryFact.user_id == user.get("user_id")).all()



    ai_reply = get_ai_response(user_message.content, db, all_memory_facts, history)

    db.add(user_message)
    message_vector = get_vector(request.content)
    new_memory = DocumentEmbedding(
        content=request.content,
        embedding=message_vector
    )
    db.add(new_memory)

    ai_message = Message(
        role="assistant",
        content=ai_reply,
        conversation_id=request.conversation_id
    )
    db.add(ai_message)
    db.commit()

    return {"ai_reply" : ai_message.content}


@chat_router.get("/chat/{conversation_id}")
async  def get_chat(user: user_dependency, db: db_dependency, conversation_id: int):
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return db.query(Message).filter(Message.conversation_id == conversation_id).all()