from sqlalchemy import Column, Integer, String, Boolean
from db import Base, engine

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String(100), nullable=False)
    status = Column(Boolean, nullable=False)

Base.metadata.create_all(engine)