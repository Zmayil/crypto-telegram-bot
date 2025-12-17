import sqlite3
import os

DB_PATH = "data/users.db"


def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS alerts
                   (
                       user_id
                       INTEGER
                       PRIMARY
                       KEY,
                       btc_threshold
                       REAL,
                       eth_threshold
                       REAL,
                       is_active
                       INTEGER
                       DEFAULT
                       1
                   )
                   ''')

    conn.commit()
    conn.close()


def set_alert(user_id: int, btc_threshold: float = None, eth_threshold: float = None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT OR REPLACE INTO alerts (user_id, btc_threshold, eth_threshold, is_active)
    VALUES (?, ?, ?, 1)
    ''', (user_id, btc_threshold, eth_threshold))

    conn.commit()
    conn.close()


def get_active_alerts():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM alerts WHERE is_active = 1')
    alerts = cursor.fetchall()

    conn.close()
    return alerts


def get_user_alerts(user_id: int):
    """Получаем уведомления конкретного пользователя"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM alerts WHERE user_id = ?', (user_id,))
    alerts = cursor.fetchall()

    conn.close()
    return alerts


def delete_alert(user_id: int, alert_type: str = None):
    """Удаляем уведомления пользователя"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if alert_type == 'btc':
        cursor.execute('UPDATE alerts SET btc_threshold = NULL WHERE user_id = ?', (user_id,))
    elif alert_type == 'eth':
        cursor.execute('UPDATE alerts SET eth_threshold = NULL WHERE user_id = ?', (user_id,))
    else:
        cursor.execute('DELETE FROM alerts WHERE user_id = ?', (user_id,))

    conn.commit()
    conn.close()