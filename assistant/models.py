
from assistant.database import Base
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, func


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String)
    last_name = Column(String)

class Conversation(Base):
    __tablename__ = 'conversations'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    started_at = Column(DateTime, default=func.now())
    user_id = Column(Integer, ForeignKey('users.id'))



class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    role = Column(String, nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())
    conversation_id = Column(Integer, ForeignKey('conversations.id'))



class MemoryFact(Base):
    __tablename__ = 'memory_facts'
    id = Column(Integer, primary_key=True)
    key = Column(String, nullable=False)
    value = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    source_message_id = Column(Integer, ForeignKey('messages.id'), nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'))


