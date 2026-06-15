from app.db_service import get_connection
from datetime import datetime, timedelta

def create_habit(user_id, name, frequency='daily'):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO habits (user_id, name, frequency) VALUES (%s, %s, %s) RETURNING id",
        (user_id, name, frequency)
    )
    habit_id = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return habit_id

def log_habit(habit_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO habit_logs (habit_id) VALUES (%s)", (habit_id,))
        conn.commit()
        success = True
    except:
        success = False
    conn.close()
    return success

def list_habits(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM habits WHERE user_id = %s", (user_id,))
    habits = cursor.fetchall()
    conn.close()
    return habits

def get_streak(habit_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT logged_at FROM habit_logs WHERE habit_id = %s ORDER BY logged_at DESC", (habit_id,))
    logs = cursor.fetchall()
    conn.close()
    
    if not logs:
        return 0
    
    streak = 0
    current_date = datetime.now().date()
    
    # Check if logged today or yesterday to continue streak
    last_log_date = logs[0][0]
    if last_log_date < current_date - timedelta(days=1):
        return 0
        
    for i in range(len(logs)):
        log_date = logs[i][0]
        expected_date = current_date - timedelta(days=streak)
        
        if streak == 0 and log_date == current_date - timedelta(days=1):
             pass
        elif log_date == expected_date:
            streak += 1
        elif log_date < expected_date:
            break
            
    return streak
