
from fastapi import  APIRouter,  HTTPException
from typing import Annotated
from fastapi import Depends
from assistant.models import Conversation
from sqlalchemy.orm import Session
from pydantic import BaseModel
from assistant.database import get_db
from assistant.routers.auth import get_current_user
from assistant.models import Message

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

conversation_router = APIRouter()

class ConversationRequest(BaseModel):
    title: str



@conversation_router.post("/conversation")
async def create_conversation(user: user_dependency, db: db_dependency, conversation_request: ConversationRequest):
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    conversation_model = Conversation(title=conversation_request.title,
                                      user_id=user.get("user_id"))
    db.add(conversation_model)
    db.commit()




@conversation_router.get("/conversation")
async def get_conversation_by_user_id(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return db.query(Conversation).filter(Conversation.user_id == user.get("user_id")).all()



@conversation_router.delete("/conversation/{conversation_id}")
async def delete_conversation_by_id(user: user_dependency, db: db_dependency, conversation_id: int):
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    db.query(Message).filter(Message.conversation_id == conversation_id).delete()
    db.query(Conversation).filter(Conversation.id == conversation_id).delete()
    db.commit()


