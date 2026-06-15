from app.db_service import get_connection

def create_task(user_id, title, description=None, due_date=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (user_id, title, description, due_date) VALUES (%s, %s, %s, %s) RETURNING id",
        (user_id, title, description, due_date)
    )
    task_id = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return task_id

def list_tasks(user_id, status=None):
    conn = get_connection()
    cursor = conn.cursor()
    if status:
        cursor.execute("SELECT * FROM tasks WHERE user_id = %s AND status = %s", (user_id, status))
    else:
        cursor.execute("SELECT * FROM tasks WHERE user_id = %s", (user_id,))
    tasks = cursor.fetchall()
    conn.close()
    return tasks

def complete_task(task_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET status = 'completed' WHERE id = %s", (task_id,))
    conn.commit()
    count = cursor.rowcount
    conn.close()
    return count > 0

def delete_task(task_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
    conn.commit()
    count = cursor.rowcount
    conn.close()
    return count > 0
