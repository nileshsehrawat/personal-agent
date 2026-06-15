from app.db_service import get_connection
from datetime import datetime

def create_event(user_id, title, start_time, end_time=None, location=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO events (user_id, title, start_time, end_time, location) VALUES (%s, %s, %s, %s, %s) RETURNING id",
        (user_id, title, start_time, end_time, location)
    )
    event_id = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return event_id

def list_events(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM events WHERE user_id = %s ORDER BY start_time ASC", (user_id,))
    events = cursor.fetchall()
    conn.close()
    return events

def upcoming_events(user_id, limit=5):
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now()
    cursor.execute(
        "SELECT * FROM events WHERE user_id = %s AND start_time >= %s ORDER BY start_time ASC LIMIT %s", 
        (user_id, now, limit)
    )
    events = cursor.fetchall()
    conn.close()
    return events
