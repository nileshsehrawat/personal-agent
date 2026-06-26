from typing import Optional
from app.agent.registry import registry
from app.agent.schemas import (
    CreateTaskArgs, ListTasksArgs, CompleteTaskArgs, DeleteTaskArgs,
    CreateHabitArgs, ListHabitsArgs, LogHabitArgs, GetHabitStreakArgs,
    CreateEventArgs, ListEventsArgs, UpcomingEventsArgs,
    AddMemoryArgs, ListMemoriesArgs, DeleteMemoryArgs
)
from app.services import (
    task_service,
    habit_service,
    event_service,
    memory_service
)

# --- TASK TOOLS ---

@registry.register_tool(
    name="create_task",
    description="Create a new task with a title, optional description, and optional due date.",
    args_schema=CreateTaskArgs,
    requires_user_id=True
)
def create_task_tool(user_id: int, title: str, description: Optional[str] = None, due_date: Optional[str] = None):
    task_id = task_service.create_task(user_id, title, description, due_date)
    return {"success": True, "task_id": task_id, "message": f"Task '{title}' created successfully."}


@registry.register_tool(
    name="list_tasks",
    description="List tasks for the user, optionally filtered by status ('pending' or 'completed').",
    args_schema=ListTasksArgs,
    requires_user_id=True
)
def list_tasks_tool(user_id: int, task_status: Optional[str] = None):
    tasks = task_service.list_tasks(user_id, task_status)
    # database tuple: (id, user_id, title, description, status, due_date, created_at)
    formatted = []
    for t in tasks:
        formatted.append({
            "id": t[0],
            "user_id": t[1],
            "title": t[2],
            "description": t[3],
            "status": t[4],
            "due_date": str(t[5]) if t[5] is not None else None,
            "created_at": str(t[6]) if t[6] is not None else None
        })
    return formatted


@registry.register_tool(
    name="complete_task",
    description="Mark a task as completed using its task ID.",
    args_schema=CompleteTaskArgs,
    requires_user_id=False
)
def complete_task_tool(task_id: str):
    try:
        id_val = int(task_id)
    except ValueError:
        return {"success": False, "message": f"Invalid task ID format: '{task_id}'. Must be a number."}
    success = task_service.complete_task(id_val)
    if success:
        return {"success": True, "message": f"Task {task_id} marked as completed."}
    return {"success": False, "message": f"Task {task_id} not found."}


@registry.register_tool(
    name="delete_task",
    description="Delete/remove a task using its task ID.",
    args_schema=DeleteTaskArgs,
    requires_user_id=False
)
def delete_task_tool(task_id: str):
    try:
        id_val = int(task_id)
    except ValueError:
        return {"success": False, "message": f"Invalid task ID format: '{task_id}'. Must be a number."}
    success = task_service.delete_task(id_val)
    if success:
        return {"success": True, "message": f"Task {task_id} deleted."}
    return {"success": False, "message": f"Task {task_id} not found."}


# --- HABIT TOOLS ---

@registry.register_tool(
    name="create_habit",
    description="Create a new habit to track, such as drinking water or exercising daily.",
    args_schema=CreateHabitArgs,
    requires_user_id=True
)
def create_habit_tool(user_id: int, name: str, frequency: str = "daily"):
    habit_id = habit_service.create_habit(user_id, name, frequency)
    return {"success": True, "habit_id": habit_id, "message": f"Habit '{name}' created successfully."}


@registry.register_tool(
    name="list_habits",
    description="List all habits tracked by the user and their current streaks.",
    args_schema=ListHabitsArgs,
    requires_user_id=True
)
def list_habits_tool(user_id: int):
    habits = habit_service.list_habits(user_id)
    # database tuple: (id, user_id, name, frequency, created_at)
    formatted = []
    for h in habits:
        streak = habit_service.get_streak(h[0])
        formatted.append({
            "id": h[0],
            "user_id": h[1],
            "name": h[2],
            "frequency": h[3],
            "streak": streak,
            "created_at": str(h[4]) if h[4] is not None else None
        })
    return formatted


@registry.register_tool(
    name="log_habit",
    description="Log/mark a habit as completed/done for today.",
    args_schema=LogHabitArgs,
    requires_user_id=False
)
def log_habit_tool(habit_id: str):
    try:
        id_val = int(habit_id)
    except ValueError:
        return {"success": False, "message": f"Invalid habit ID format: '{habit_id}'. Must be a number."}
    success = habit_service.log_habit(id_val)
    if success:
        return {"success": True, "message": f"Habit {habit_id} logged successfully for today."}
    return {"success": False, "message": f"Could not log habit {habit_id}. It may already be logged for today or does not exist."}


@registry.register_tool(
    name="get_habit_streak",
    description="Get the current daily/weekly streak count for a habit.",
    args_schema=GetHabitStreakArgs,
    requires_user_id=False
)
def get_habit_streak_tool(habit_id: str):
    try:
        id_val = int(habit_id)
    except ValueError:
        return {"success": False, "message": f"Invalid habit ID format: '{habit_id}'. Must be a number."}
    streak = habit_service.get_streak(id_val)
    return {"habit_id": habit_id, "streak": streak}


# --- EVENT TOOLS ---

@registry.register_tool(
    name="create_event",
    description="Create/schedule a new event or appointment with a title, start time, optional end time, and optional location.",
    args_schema=CreateEventArgs,
    requires_user_id=True
)
def create_event_tool(user_id: int, title: str, start_time: str, end_time: Optional[str] = None, location: Optional[str] = None):
    event_id = event_service.create_event(user_id, title, start_time, end_time, location)
    return {"success": True, "event_id": event_id, "message": f"Event '{title}' scheduled successfully."}


@registry.register_tool(
    name="list_events",
    description="List all scheduled events for the user.",
    args_schema=ListEventsArgs,
    requires_user_id=True
)
def list_events_tool(user_id: int):
    events = event_service.list_events(user_id)
    # database tuple: (id, user_id, title, start_time, end_time, location, created_at)
    formatted = []
    for e in events:
        formatted.append({
            "id": e[0],
            "user_id": e[1],
            "title": e[2],
            "start_time": str(e[3]) if e[3] is not None else None,
            "end_time": str(e[4]) if e[4] is not None else None,
            "location": e[5],
            "created_at": str(e[6]) if e[6] is not None else None
        })
    return formatted


@registry.register_tool(
    name="upcoming_events",
    description="Retrieve upcoming events starting from now.",
    args_schema=UpcomingEventsArgs,
    requires_user_id=True
)
def upcoming_events_tool(user_id: int, limit: int = 5):
    events = event_service.upcoming_events(user_id, limit)
    # database tuple: (id, user_id, title, start_time, end_time, location, created_at)
    formatted = []
    for e in events:
        formatted.append({
            "id": e[0],
            "user_id": e[1],
            "title": e[2],
            "start_time": str(e[3]) if e[3] is not None else None,
            "end_time": str(e[4]) if e[4] is not None else None,
            "location": e[5],
            "created_at": str(e[6]) if e[6] is not None else None
        })
    return formatted


# --- MEMORY TOOLS ---

@registry.register_tool(
    name="add_memory",
    description="Store an important fact or piece of information about the user for long-term memory/recall.",
    args_schema=AddMemoryArgs,
    requires_user_id=True
)
def add_memory_tool(user_id: int, content: str, importance: int = 1):
    memory_id = memory_service.add_memory(user_id, content, importance)
    return {"success": True, "memory_id": memory_id, "message": "Information saved to long-term memory."}


@registry.register_tool(
    name="list_memories",
    description="List all stored memories and facts about the user.",
    args_schema=ListMemoriesArgs,
    requires_user_id=True
)
def list_memories_tool(user_id: int):
    memories = memory_service.list_memories(user_id)
    # database tuple: (id, user_id, content, importance, created_at)
    formatted = []
    for m in memories:
        formatted.append({
            "id": m[0],
            "user_id": m[1],
            "content": m[2],
            "importance": m[3],
            "created_at": str(m[4]) if m[4] is not None else None
        })
    return formatted


@registry.register_tool(
    name="delete_memory",
    description="Delete a stored memory or fact by its ID.",
    args_schema=DeleteMemoryArgs,
    requires_user_id=False
)
def delete_memory_tool(memory_id: str):
    try:
        id_val = int(memory_id)
    except ValueError:
        return {"success": False, "message": f"Invalid memory ID format: '{memory_id}'. Must be a number."}
    success = memory_service.delete_memory(id_val)
    if success:
        return {"success": True, "message": f"Memory {memory_id} deleted."}
    return {"success": False, "message": f"Memory {memory_id} not found."}
