from pydantic import BaseModel, Field
from typing import Optional

# Tasks Tool Arguments
class CreateTaskArgs(BaseModel):
    title: str = Field(..., description="The title of the task (e.g. 'Buy milk')")
    description: Optional[str] = Field(None, description="Optional detailed description of the task")
    due_date: Optional[str] = Field(None, description="Optional due date in ISO format or YYYY-MM-DD")

class ListTasksArgs(BaseModel):
    task_status: Optional[str] = Field(None, description="Filter tasks by status: 'pending' or 'completed'")

class CompleteTaskArgs(BaseModel):
    task_id: str = Field(..., description="The unique ID of the task to complete")

class DeleteTaskArgs(BaseModel):
    task_id: str = Field(..., description="The unique ID of the task to delete")

# Habits Tool Arguments
class ListHabitsArgs(BaseModel):
    pass

class CreateHabitArgs(BaseModel):
    name: str = Field(..., description="The name of the habit (e.g. 'Read a book')")
    frequency: Optional[str] = Field("daily", description="Frequency of the habit: 'daily', 'weekly', etc.")

class LogHabitArgs(BaseModel):
    habit_id: str = Field(..., description="The unique ID of the habit to log for today")

class GetHabitStreakArgs(BaseModel):
    habit_id: str = Field(..., description="The unique ID of the habit to check streak for")

# Events Tool Arguments
class CreateEventArgs(BaseModel):
    title: str = Field(..., description="The title of the event (e.g. 'Dentist appointment')")
    start_time: str = Field(..., description="The start time of the event (format: YYYY-MM-DD HH:MM:SS or ISO format)")
    end_time: Optional[str] = Field(None, description="Optional end time of the event")
    location: Optional[str] = Field(None, description="Optional physical or virtual location of the event")

class ListEventsArgs(BaseModel):
    pass

class UpcomingEventsArgs(BaseModel):
    limit: Optional[int] = Field(5, description="Maximum number of upcoming events to retrieve")

# Memories Tool Arguments
class AddMemoryArgs(BaseModel):
    content: str = Field(..., description="The content/fact to remember about the user")
    importance: Optional[int] = Field(1, description="Importance level from 1 to 5 (default: 1)")

class ListMemoriesArgs(BaseModel):
    pass

class DeleteMemoryArgs(BaseModel):
    memory_id: str = Field(..., description="The unique ID of the memory to delete")
