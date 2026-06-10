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

# --- COMMAND ROUTER ---
def handle_command(command_text: str, user_id: int, username: str):
    parts = command_text.split(" ", 1)
    cmd = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""

    if cmd == "/start":
        return (
            f"Hello {username}! I'm your Personal Agent.\n\n"
            "*Available Commands:*\n"
            "📅 /today - Daily overview\n"
            "📝 /tasks - List pending tasks\n"
            "➕ /addtask <title> - Create task\n"
            "✅ /done <id> - Complete task\n"
            "🔥 /addhabit <name> - Create habit\n"
            "🪵 /log - List & log habits\n"
            "💡 /addmemory <text> - Save memory"
        )

    if cmd == "/today":
        tasks = task_service.list_tasks(user_id, status='pending')
        events = event_service.upcoming_events(user_id, limit=3)
        habits = habit_service.list_habits(user_id)
        memories = memory_service.list_memories(user_id)

        summary = f"Good Day, {username}!\n\n"
        
        summary += "📝 *Tasks*\n"
        if tasks:
            summary += "\n".join([f"□ {t[2]}" for t in tasks])
        else:
            summary += "No pending tasks."
        
        summary += "\n\n📅 *Upcoming Events*\n"
        if events:
            summary += "\n".join([f"• {e[2]} ({e[3]})" for e in events])
        else:
            summary += "No upcoming events."

        summary += "\n\n🔥 *Habit Streaks*\n"
        if habits:
            habit_list = []
            for h in habits:
                streak = habit_service.get_streak(h[0])
                habit_list.append(f"{h[2]}: {streak} days")
            summary += "\n".join(habit_list)
        else:
            summary += "No habits tracked."

        summary += "\n\n💡 *Memories*\n"
        if memories:
            summary += "\n".join([f"• {m[2]}" for m in memories[:3]])
        else:
            summary += "No memories yet."
            
        return summary

    if cmd == "/addtask":
        if not args: return "Usage: /addtask <task title>"
        task_id = task_service.create_task(user_id, args)
        return f"Task added! (ID: {task_id})"

    if cmd == "/tasks":
        tasks = task_service.list_tasks(user_id, status='pending')
        if not tasks: return "You have no pending tasks."
        return "*Your Tasks:*\n" + "\n".join([f"{t[0]}. {t[2]}" for t in tasks])

    if cmd == "/done":
        if not args: return "Usage: /done <task id>"
        success = task_service.complete_task(int(args))
        return "Task marked as completed!" if success else "Task not found."

    if cmd == "/addhabit":
        if not args: return "Usage: /addhabit <habit name>"
        habit_id = habit_service.create_habit(user_id, args)
        return f"Habit '{args}' created!"

    if cmd == "/log":
        habits = habit_service.list_habits(user_id)
        if not args:
            if not habits: return "No habits to log. Create one with /addhabit"
            return "Usage: /log <habit id>\n" + "\n".join([f"{h[0]}: {h[2]}" for h in habits])
        success = habit_service.log_habit(int(args))
        return "Habit logged!" if success else "Already logged today or invalid ID."

    if cmd == "/addmemory":
        if not args: return "Usage: /addmemory <content>"
        memory_service.add_memory(user_id, args)
        return "Memory saved!"

    return None # Not a recognized command

# --- TELEGRAM WEBHOOK ---
@app.get("/webhook")
def webhook_info():
    return {"message": "Telegram Webhook is active and waiting for POST requests."}

@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    try:
        if "message" in data:
            message_text = data["message"].get("text", "")
            chat_id = data["message"]["chat"]["id"]
            username = data["message"]["chat"].get("username", data["message"]["chat"].get("first_name", "User"))

            # Register/Get user using user_service
            user_id = user_service.get_or_create_user(chat_id, username)

            if message_text:
                # 1. Try Command Router first (Phase 2)
                if message_text.startswith("/"):
                    response = handle_command(message_text, user_id, username)
                    if response:
                        send_message(chat_id, response)
                        return {"ok": True}

                # 2. Fallback to AI (Phase 4)
                response = ask_llm(message_text)
                send_message(chat_id, response)

    except Exception as e:
        print(f"Webhook error: {e}")

    return {"ok": True}

# --- EXISTING ENDPOINTS ---
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

@app.post("/events", response_model=int)
def create_event_endpoint(event: EventCreate):
    return event_service.create_event(event.user_id, event.title, event.start_time, event.end_time, event.location)

@app.get("/events/{user_id}")
def list_events_endpoint(user_id: int):
    return event_service.list_events(user_id)

@app.get("/events/{user_id}/upcoming")
def upcoming_events_endpoint(user_id: int, limit: int = 5):
    return event_service.upcoming_events(user_id, limit)

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

@app.get("/test")
def test():
    answer = ask_llm("Say hello in one sentence")
    return {"response": answer}
