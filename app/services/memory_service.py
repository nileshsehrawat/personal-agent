from app.db_service import get_connection

def add_memory(user_id, content, importance=1):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO memories (user_id, content, importance) VALUES (?, ?, ?)",
        (user_id, content, importance)
    )
    conn.commit()
    memory_id = cursor.lastrowid
    conn.close()
    return memory_id

def list_memories(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM memories WHERE user_id = ? ORDER BY importance DESC, created_at DESC", (user_id,))
    memories = cursor.fetchall()
    conn.close()
    return memories

def delete_memory(memory_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
    conn.commit()
    changes = conn.total_changes
    conn.close()
    return changes > 0
