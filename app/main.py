from fastapi import FastAPI, Request, HTTPException
from typing import List, Optional

from app.llm_service import ask_llm
from app.telegram_service import send_message
from app.db_service import init_db
from app.services import (
    user_service,
    task_service,
    habit_service,
    event_service,
    memory_service
)
from app.schemas import (
    TaskCreate, TaskResponse,
    HabitCreate, HabitResponse,
    EventCreate, EventResponse,
    MemoryCreate, MemoryResponse
)

app = FastAPI(title="Personal Agent API")

# Initialize database on startup
init_db()

@app.get("/")
def root():
    return {"status": "running", "message": "Personal Agent API is active"}

# --- TASK ENDPOINTS ---
@app.post("/tasks", response_model=int)
def create_task_endpoint(task: TaskCreate):
    return task_service.create_task(task.user_id, task.title, task.description, task.due_date)

@app.get("/tasks/{user_id}")
def list_tasks_endpoint(user_id: int, status: Optional[str] = None):
    return task_service.list_tasks(user_id, status)

@app.put("/tasks/{task_id}/complete")
def complete_task_endpoint(task_id: int):
    success = task_service.complete_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task marked as completed"}

@app.delete("/tasks/{task_id}")
def delete_task_endpoint(task_id: int):
    success = task_service.delete_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully"}

# --- HABIT ENDPOINTS ---
@app.post("/habits", response_model=int)
def create_habit_endpoint(habit: HabitCreate):
    return habit_service.create_habit(habit.user_id, habit.name, habit.frequency)

@app.get("/habits/{user_id}")
def list_habits_endpoint(user_id: int):
    return habit_service.list_habits(user_id)

@app.post("/habits/{habit_id}/log")
def log_habit_endpoint(habit_id: int):
    success = habit_service.log_habit(habit_id)
    if not success:
        return {"message": "Already logged today or habit not found"}
    return {"message": "Habit logged successfully"}

@app.get("/habits/{habit_id}/streak")
def get_habit_streak_endpoint(habit_id: int):
    streak = habit_service.get_streak(habit_id)
    return {"habit_id": habit_id, "streak": streak}

# --- EVENT ENDPOINTS ---
@app.post("/events", response_model=int)
def create_event_endpoint(event: EventCreate):
    return event_service.create_event(event.user_id, event.title, event.start_time, event.end_time, event.location)

@app.get("/events/{user_id}")
def list_events_endpoint(user_id: int):
    return event_service.list_events(user_id)

@app.get("/events/{user_id}/upcoming")
def upcoming_events_endpoint(user_id: int, limit: int = 5):
    return event_service.upcoming_events(user_id, limit)

# --- MEMORY ENDPOINTS ---
@app.post("/memories", response_model=int)
def create_memory_endpoint(memory: MemoryCreate):
    return memory_service.add_memory(memory.user_id, memory.content, memory.importance)

@app.get("/memories/{user_id}")
def list_memories_endpoint(user_id: int):
    return memory_service.list_memories(user_id)

@app.delete("/memories/{memory_id}")
def delete_memory_endpoint(memory_id: int):
    success = memory_service.delete_memory(memory_id)
    if not success:
        raise HTTPException(status_code=404, detail="Memory not found")
    return {"message": "Memory deleted successfully"}

# --- TELEGRAM WEBHOOK ---
@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    try:
        if "message" in data:
            message_text = data["message"].get("text", "")
            chat_id = data["message"]["chat"]["id"]
            username = data["message"]["chat"].get("username", "Unknown")

            # Register/Get user using user_service
            user_id = user_service.get_or_create_user(chat_id, username)

            if message_text:
                response = ask_llm(message_text)
                send_message(chat_id, response)

    except Exception as e:
        print(f"Webhook error: {e}")

    return {"ok": True}

@app.get("/test")
def test():
    answer = ask_llm("Say hello in one sentence")
    return {"response": answer}
