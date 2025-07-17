from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    points = Column(Integer, default=0)
    rank = Column(String, default="Bronze")

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    type = Column(String) # MCQ, BUG_FIX, PREDICT_OUTPUT
    difficulty = Column(String)
    options = Column(String, nullable=True) # JSON string for MCQs
    correct_answer = Column(String)

# Powered by Innovate CLI, a product of vaidik.co
