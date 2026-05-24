
from fastapi import APIRouter, HTTPException
from typing import Annotated
from fastapi import Depends
from assistant.models import MemoryFact
from sqlalchemy.orm import Session
from pydantic import BaseModel
from assistant.database import get_db
from assistant.routers.auth import get_current_user

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

memory_fact_router = APIRouter()

class MemoryFactRequest(BaseModel):
    key: str
    value: str



@memory_fact_router.post("/memoryfact")
async def create_memory_fact(user: user_dependency, db: db_dependency, memory_fact_request: MemoryFactRequest):
    if user is None:
        raise HTTPException(status_code = 401, detail="User not found")
    memory_fact_model = MemoryFact(key=memory_fact_request.key,
                                   value=memory_fact_request.value,
                                   user_id=user.get("user_id"))
    db.add(memory_fact_model)
    db.commit()




@memory_fact_router.delete("/memoryfact/{memory_id}")
async def delete_memory_fact_by_id(user: user_dependency, db: db_dependency, memory_id: int):
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    db.query(MemoryFact).filter(MemoryFact.id == memory_id).delete()
    db.commit()

@memory_fact_router.delete("/memoryfact/users_id")
async def delete_memory_fact_by_user_id(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    db.query(MemoryFact).filter(MemoryFact.user_id == user.get("user_id")).delete()
    db.commit()