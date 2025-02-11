from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

def get_session_factory(uri):
    engine = create_engine(uri, pool_pre_ping=True)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)
    
Base = declarative_base()

class UserMessage(Base):
    __tablename__ = 'user_message'
    id = Column(Integer, primary_key=True)
    type = Column(String(255), nullable=False, default="NORMAL")
    message = Column(String(3000), nullable=True)
    smsbody = Column(JSON, nullable=True)
    from_phone = Column(String(255), nullable=True)
    to_phone = Column(String(255), nullable=True)
    is_deleted = Column(Boolean, default=False)
    thread_result = Column(String(3000), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    media = relationship("UserMedia", back_populates="user_message", cascade="all, delete-orphan")
    asana_task = relationship("AsanaTask", back_populates="user_message", uselist=False)

class UserMedia(Base):
    __tablename__ = 'user_media'
    id = Column(Integer, primary_key=True)
    user_message_id = Column(Integer, ForeignKey('user_message.id', ondelete='CASCADE'), nullable=False)
    media_url = Column(String(1000), nullable=False)
    media_location = Column(String(255), nullable=False)
    translation_text = Column(String(3000), nullable=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    user_message = relationship("UserMessage", back_populates="media")

class AsanaTask(Base):
    __tablename__ = 'asana_task'
    id = Column(Integer, primary_key=True)
    task_id = Column(String(255), nullable=False)
    workspace_id = Column(String(255), nullable=False)
    project_id = Column(String(255), nullable=False)
    task_name = Column(String(255), nullable=False)
    task_notes = Column(String(3000), nullable=True)
    is_deleted = Column(Boolean, default=False)
    user_message_id = Column(Integer, ForeignKey('user_message.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    user_message = relationship("UserMessage", back_populates="asana_task")

def init_db(uri):
    engine = create_engine(uri, pool_pre_ping=True)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)