from app.db_service import get_connection

def add_memory(user_id, content, importance=1):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO memories (user_id, content, importance) VALUES (%s, %s, %s) RETURNING id",
        (user_id, content, importance)
    )
    memory_id = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return memory_id

def list_memories(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM memories WHERE user_id = %s ORDER BY importance DESC, created_at DESC", (user_id,))
    memories = cursor.fetchall()
    conn.close()
    return memories

def delete_memory(memory_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM memories WHERE id = %s", (memory_id,))
    conn.commit()
    count = cursor.rowcount
    conn.close()
    return count > 0
