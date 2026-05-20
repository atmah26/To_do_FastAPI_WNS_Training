from pydantic import BaseModel, field_validator, model_validator
from typing import Optional
import re

class TaskCreate(BaseModel):
    description : str
    status : bool
    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Description cannot be empty or whitespace.")
        if len(v) < 3:
            raise ValueError("Description must be at least 3 characters long.")
        if len(v) > 100:
            raise ValueError("Description cannot exceed 100 characters.")
        if not re.search(r"[a-zA-Z]", v):
            raise ValueError("Description must contain at least one letter.")
        return v[0].upper() + v[1:]

class TaskResponse(BaseModel):
    id : int
    description : str
    status : bool

    class Config:
        from_attributes = True