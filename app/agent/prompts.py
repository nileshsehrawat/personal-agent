from datetime import datetime
from typing import Optional

def get_system_prompt(current_time: Optional[str] = None) -> str:
    """
    Generates a minimal system prompt containing only the assistant persona and current date/time.
    This prevents Llama 3.3 formatting drift to XML tool calls.
    """
    if not current_time:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    return f"You are a helpful and smart Personal Assistant AI Agent. The current date and time is: {current_time}."
