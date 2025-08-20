import mysql.connector
from datetime import datetime

# --- Asetukset ---
DB_HOST = "127.0.0.1"
DB_USER = "root"
DB_PASSWORD = "test"
DB_NAME = "work_tracking"

# --- Yhteysfunktio ---
def get_connection():
    return mysql.connector.connect(
         host="127.0.0.1",
         user="root",
        password="test",
        database="work_tracking"
    )

# --- Funktiot ---
def aloita_tyovuoro(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    sql = "INSERT INTO work_sessions (user_id, start_time) VALUES (%s, %s)"
    cursor.execute(sql, (user_id, datetime.now()))
    conn.commit()
    print(f"Työvuoro aloitettu (user_id={user_id}), session_id={cursor.lastrowid}")
    cursor.close()
    conn.close()
    return cursor.lastrowid

def lopeta_tyovuoro(session_id):
    conn = get_connection()
    cursor = conn.cursor()
    sql = """
        UPDATE work_sessions
        SET end_time = %s,
            duration_minutes = TIMESTAMPDIFF(MINUTE, start_time, %s)
        WHERE id = %s
    """
    now = datetime.now()
    cursor.execute(sql, (now, now, session_id))
    conn.commit()
    print(f"Työvuoro lopetettu (session_id={session_id})")
    cursor.close()
    conn.close()

def aloita_kierros(user_id, site_id):
    conn = get_connection()
    cursor = conn.cursor()
    sql = "INSERT INTO site_visits (user_id, site_id, start_time) VALUES (%s, %s, %s)"
    cursor.execute(sql, (user_id, site_id, datetime.now()))
    conn.commit()
    print(f"Kierros aloitettu (site_id={site_id}), visit_id={cursor.lastrowid}")
    cursor.close()
    conn.close()
    return cursor.lastrowid

def lopeta_kierros(visit_id):
    conn = get_connection()
    cursor = conn.cursor()
    sql = """
        UPDATE site_visits
        SET end_time = %s,
            duration_minutes = TIMESTAMPDIFF(MINUTE, start_time, %s)
        WHERE id = %s
    """
    now = datetime.now()
    cursor.execute(sql, (now, now, visit_id))
    conn.commit()
    print(f"Kierros lopetettu (visit_id={visit_id})")
    cursor.close()
    conn.close()

def lisaa_tapahtuma(visit_id, event_type, description, photo_path=None):
    conn = get_connection()
    cursor = conn.cursor()
    sql = """
        INSERT INTO events (site_visit_id, event_type, description, photo_path)
        VALUES (%s, %s, %s, %s)
    """
    cursor.execute(sql, (visit_id, event_type, description, photo_path))
    conn.commit()
    print(f"Tapahtuma lisätty (visit_id={visit_id})")
    cursor.close()
    conn.close()

# --- Testaus ---
if __name__ == "__main__":
    # Esimerkkitestaus:
    USER_ID = 1  # Muuta oman users-taulun ID:n mukaan
    SITE_ID = 1  # Muuta oman sites-taulun ID:n mukaan

    # Aloitetaan työvuoro
    session_id = aloita_tyovuoro(USER_ID)

    # Aloitetaan kierros
    visit_id = aloita_kierros(USER_ID, SITE_ID)

    # Lisätään tapahtuma kierrokselle
    lisaa_tapahtuma(visit_id, "Huoltotarve", "Lamppu pimeänä porraskäytävässä", None)

    # Lopetetaan kierros
    lopeta_kierros(visit_id)

    # Lopetetaan työvuoro
    lopeta_tyovuoro(session_id)
