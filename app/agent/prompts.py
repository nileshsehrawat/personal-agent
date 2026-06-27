from datetime import datetime
from typing import Optional, List, Any

def get_system_prompt(
    current_time: Optional[str] = None,
    memories: Optional[List[Any]] = None,
    tasks: Optional[List[Any]] = None,
    events: Optional[List[Any]] = None
) -> str:
    """
    Generates the system prompt for the AI Agent, including the current timestamp and injected context.
    
    Args:
        current_time: Current timestamp to resolve relative times.
        memories: Optional list of memory tuples.
        tasks: Optional list of task tuples.
        events: Optional list of event tuples.
    """
    if not current_time:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    prompt = f"You are a helpful and smart Personal Assistant AI Agent. The current date and time is: {current_time}."
    
    context_blocks = []
    
    if memories:
        mem_lines = []
        for m in memories:
            # memory tuple format: (id, user_id, content, importance, created_at)
            mem_lines.append(f"- [Memory ID: {m[0]}] {m[2]}")
        context_blocks.append("### USER PROFILE & MEMORIES\n" + "\n".join(mem_lines))
        
    if tasks:
        task_lines = []
        for t in tasks:
            # task tuple format: (id, user_id, title, description, status, due_date, created_at)
            due = f" (Due: {t[5]})" if t[5] else ""
            task_lines.append(f"- [Task ID: {t[0]}] {t[2]}{due}")
        context_blocks.append("### PENDING TASKS\n" + "\n".join(task_lines))
        
    if events:
        event_lines = []
        for e in events:
            # event tuple format: (id, user_id, title, start_time, end_time, location, created_at)
            loc = f" at {e[5]}" if e[5] else ""
            event_lines.append(f"- [Event ID: {e[0]}] {e[2]} @ {e[3]}{loc}")
        context_blocks.append("### UPCOMING EVENTS\n" + "\n".join(event_lines))
        
    if context_blocks:
        prompt += (
            "\n\nUse the following user context to answer questions directly when possible. "
            "When the user asks you to modify, complete, or delete an existing task, event, or memory, "
            "refer to the IDs below:\n\n" + "\n\n".join(context_blocks)
        )
        
    return prompt
