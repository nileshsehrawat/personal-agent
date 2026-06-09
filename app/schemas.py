from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Task Schemas
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[str] = None

class TaskCreate(TaskBase):
    user_id: int

class TaskResponse(TaskBase):
    id: int
    user_id: int
    status: str
    created_at: str

# Habit Schemas
class HabitBase(BaseModel):
    name: str
    frequency: Optional[str] = "daily"

class HabitCreate(HabitBase):
    user_id: int

class HabitResponse(HabitBase):
    id: int
    user_id: int
    created_at: str

# Event Schemas
class EventBase(BaseModel):
    title: str
    start_time: str
    end_time: Optional[str] = None
    location: Optional[str] = None

class EventCreate(EventBase):
    user_id: int

class EventResponse(EventBase):
    id: int
    user_id: int
    created_at: str

# Memory Schemas
class MemoryBase(BaseModel):
    content: str
    importance: Optional[int] = 1

class MemoryCreate(MemoryBase):
    user_id: int

class MemoryResponse(MemoryBase):
    id: int
    user_id: int
    created_at: str
