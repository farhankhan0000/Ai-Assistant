from fastapi import HTTPException, status
from fastapi import APIRouter
from typing import Annotated
from fastapi import Depends
from assistant.models import User
from sqlalchemy.orm import Session
from pydantic import BaseModel
from assistant.database import get_db
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime,timedelta, timezone
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")


db_dependency = Annotated[Session, Depends(get_db)]

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/auth/login")


auth_router = APIRouter()


class UserRequest(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str



SECRET_KEY = 'AI_EXPRESS'
algorithm = 'HS256'

def user_verification(db, user_email: str, user_password: str):
    user = db.query(User).filter(User.email==user_email).first()
    if not user:
        return False
    if not bcrypt_context.verify(user_password, user.hashed_password):
        return False
    return user

def create_access_token(user_id: int, email: str, exp_time: timedelta):
    payload = {
        "id" : user_id,
        "email" : email,
        "exp" : datetime.now(timezone.utc) + exp_time
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=algorithm)

def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[algorithm])
        user_id = payload.get("id")
        user_email = payload.get("email")

        if user_id is None or user_email is None:
            raise HTTPException(status_code=401, detail="User not found")

        return {"user_id" : user_id, "user_email" : user_email}

    except JWTError:
        raise HTTPException(status_code=401, detail="User not found")







@auth_router.post("/auth/register", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, user_request: UserRequest):
    hashed_password = bcrypt_context.hash(user_request.password)
    user_model = User(email = user_request.email,
                      hashed_password = hashed_password,
                      first_name = user_request.first_name,
                      last_name = user_request.last_name)
    db.add(user_model)
    db.commit()

@auth_router.post("/auth/login", status_code=status.HTTP_200_OK)
async def get_token(db: db_dependency, form_data: OAuth2PasswordRequestForm = Depends()):
    user = user_verification(db, form_data.username, form_data.password)
    if user is False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="user not found")
    token = create_access_token(user.id, user.email, timedelta(days=1))
    return {"access_token" : token, "token_type" : "bearer"}