
from fastapi import FastAPI
from assistant.routers.auth import auth_router as auth_router
from assistant.routers.conversations import conversation_router as conversation_router
from assistant.routers.memory_facts import memory_fact_router as memory_fact_router
from assistant.database import engine,Base
from assistant.routers.chat import chat_router as chat_router
app = FastAPI()

app.include_router(auth_router)
app.include_router(conversation_router)
app.include_router(memory_fact_router)
app.include_router(chat_router)


Base.metadata.create_all(bind=engine)















