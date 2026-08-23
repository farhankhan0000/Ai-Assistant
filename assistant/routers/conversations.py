
from fastapi import  APIRouter,  HTTPException, status
from typing import Annotated
from fastapi import Depends
from assistant.models import Conversation
from sqlalchemy.orm import Session
from pydantic import BaseModel
from assistant.database import get_db
from assistant.routers.auth import get_current_user
from assistant.models import Message
from assistant.ai import  get_ai_title

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

conversation_router = APIRouter()

class ConversationRequest(BaseModel):
    title: str

class UserRequest(BaseModel):
    conversation_id: int
    user_message: str



@conversation_router.post("/conversation", status_code=status.HTTP_201_CREATED)
async def create_conversation(user: user_dependency, db: db_dependency, conversation_request: ConversationRequest):
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    conversation_model = Conversation(title=conversation_request.title,
                                      user_id=user.get("user_id"))
    db.add(conversation_model)
    db.commit()
    return {"id" : conversation_model.id, "title" : conversation_model.title}



@conversation_router.get("/conversation", status_code=status.HTTP_200_OK)
async def get_conversation_by_user_id(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return db.query(Conversation).filter(Conversation.user_id == user.get("user_id")).all()



@conversation_router.delete("/conversation/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation_by_id(user: user_dependency, db: db_dependency, conversation_id: int):
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    db.query(Message).filter(Message.conversation_id == conversation_id).delete()
    db.query(Conversation).filter(Conversation.id == conversation_id).delete()
    db.commit()

@conversation_router.put("/conversation", status_code=status.HTTP_200_OK)
async def edit_conversation_title(user: user_dependency, db: db_dependency, request: UserRequest):
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    conversation = db.query(Conversation).filter(Conversation.id == request.conversation_id).first()
    if conversation is None:
        raise HTTPException(status_code=403, detail="Conversation is Wrong")

    new_title = get_ai_title(request.user_message)
    conversation.title = new_title
    db.commit()
    db.refresh(conversation)
    return {"new_title" : conversation.title}



