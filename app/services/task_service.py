from app.db_service import get_connection

def create_task(user_id, title, description=None, due_date=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (user_id, title, description, due_date) VALUES (?, ?, ?, ?)",
        (user_id, title, description, due_date)
    )
    conn.commit()
    task_id = cursor.lastrowid
    conn.close()
    return task_id

def list_tasks(user_id, status=None):
    conn = get_connection()
    cursor = conn.cursor()
    if status:
        cursor.execute("SELECT * FROM tasks WHERE user_id = ? AND status = ?", (user_id, status))
    else:
        cursor.execute("SELECT * FROM tasks WHERE user_id = ?", (user_id,))
    tasks = cursor.fetchall()
    conn.close()
    return tasks

def complete_task(task_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET status = 'completed' WHERE id = ?", (task_id,))
    conn.commit()
    changes = conn.total_changes
    conn.close()
    return changes > 0

def delete_task(task_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    changes = conn.total_changes
    conn.close()
    return changes > 0
