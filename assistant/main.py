from fastapi.responses import FileResponse
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from assistant.routers.auth import auth_router as auth_router
from assistant.routers.conversations import conversation_router as conversation_router
from assistant.database import engine,Base
from assistant.routers.chat import chat_router as chat_router
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(lifespan=lifespan)

origins = [
        "http://localhost:63342",
        "http://127.0.0.1:63342",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
def read_root():
    return FileResponse("frontend/welcome.html")



app.include_router(auth_router)
app.include_router(conversation_router)
app.include_router(chat_router)

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
















