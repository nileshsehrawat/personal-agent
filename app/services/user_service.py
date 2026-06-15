from app.db_service import get_connection

def get_or_create_user(telegram_id, username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE telegram_id = %s", (telegram_id,))
    user = cursor.fetchone()
    
    if not user:
        cursor.execute(
            "INSERT INTO users (telegram_id, username) VALUES (%s, %s) RETURNING id", 
            (telegram_id, username)
        )
        user_id = cursor.fetchone()[0]
        conn.commit()
    else:
        user_id = user[0]
        
    conn.close()
    return user_id

def get_user_by_telegram_id(telegram_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE telegram_id = %s", (telegram_id,))
    user = cursor.fetchone()
    conn.close()
    return user
