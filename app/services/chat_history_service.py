from app.db_service import get_connection
from typing import List, Dict, Any

def add_chat_message(user_id: int, role: str, content: str) -> None:
    """
    Persists a chat message (role: 'user' or 'assistant') to the database.
    """
    if not content:
        return
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO chat_history (user_id, role, content) VALUES (%s, %s, %s)",
        (user_id, role, content)
    )
    conn.commit()
    conn.close()

def get_chat_history(user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Retrieves the last N messages of chat history for a user in chronological order.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT role, content FROM chat_history WHERE user_id = %s ORDER BY created_at DESC LIMIT %s",
        (user_id, limit)
    )
    rows = cursor.fetchall()
    conn.close()
    
    # Reverse to get chronological order (oldest to newest)
    messages = []
    for r in reversed(rows):
        messages.append({"role": r[0], "content": r[1]})
    return messages

def clear_chat_history(user_id: int) -> None:
    """
    Clears all chat history for a given user.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chat_history WHERE user_id = %s", (user_id,))
    conn.commit()
    conn.close()
