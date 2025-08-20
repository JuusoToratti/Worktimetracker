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
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

# --- Apufunktio: hae käyttäjä ---
def hae_kayttaja(name, password_hash):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE name = %s AND password_hash = %s", (name, password_hash))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    else:
        return None

# --- Toiminnot ---
def aloita_tyovuoro(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO work_sessions (user_id, start_time) VALUES (%s, %s)",
        (user_id, datetime.now())
    )
    conn.commit()
    session_id = cursor.lastrowid
    print(f" Työvuoro aloitettu (session_id={session_id})")
    cursor.close()
    conn.close()
    return session_id

def lopeta_tyovuoro(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id FROM work_sessions
        WHERE user_id = %s AND end_time IS NULL
        ORDER BY start_time DESC
        LIMIT 1
    """, (user_id,))
    result = cursor.fetchone()
    if not result:
        print(" Ei avoinna olevaa työvuoroa.")
        conn.close()
        return None

    session_id = result[0]
    now = datetime.now()
    cursor.execute("""
        UPDATE work_sessions
        SET end_time = %s,
            duration_minutes = TIMESTAMPDIFF(MINUTE, start_time, %s)
        WHERE id = %s
    """, (now, now, session_id))
    conn.commit()
    print(f" Työvuoro lopetettu (session_id={session_id})")
    cursor.close()
    conn.close()
    return session_id

def aloita_kierros(user_id, site_address):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM sites WHERE address = %s", (site_address,))
    result = cursor.fetchone()
    if not result:
        print(" Kohdetta ei löytynyt annetulla osoitteella!")
        conn.close()
        return None
    site_id = result[0]

    sql = "INSERT INTO site_visits (user_id, site_id, start_time) VALUES (%s, %s, %s)"
    cursor.execute(sql, (user_id, site_id, datetime.now()))
    conn.commit()
    visit_id = cursor.lastrowid
    conn.close()
    print(f" Kierros aloitettu kohteessa '{site_address}', visit_id={visit_id}")
    return visit_id

def lopeta_kierros(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id FROM site_visits 
        WHERE user_id = %s AND end_time IS NULL
        ORDER BY start_time DESC
        LIMIT 1
    """, (user_id,))
    result = cursor.fetchone()
    if not result:
        print(" Ei avoinna olevaa kierrosta.")
        conn.close()
        return None

    visit_id = result[0]
    sql = "UPDATE site_visits SET end_time = %s WHERE id = %s"
    cursor.execute(sql, (datetime.now(), visit_id))
    conn.commit()
    conn.close()
    print(f" Kierros (visit_id={visit_id}) lopetettu onnistuneesti.")
    return visit_id

def lisaa_tapahtuma(visit_id, event_type, description, photo_path=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO events (site_visit_id, event_type, description, photo_path)
        VALUES (%s, %s, %s, %s)
        """,
        (visit_id, event_type, description, photo_path)
    )
    conn.commit()
    print(f" Tapahtuma lisätty (visit_id={visit_id})")
    cursor.close()
    conn.close()
    # --- Näyttöfunktiot ---
def nayta_tyovuorot():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ws.id, u.name, ws.start_time, ws.end_time, ws.duration_minutes
        FROM work_sessions ws
        JOIN users u ON ws.user_id = u.id
        ORDER BY ws.start_time DESC
    """)
    print("\n--- Työvuorot ---")
    for row in cursor.fetchall():
        print(f"Vuoro ID={row[0]} | Käyttäjä={row[1]} | Alku={row[2]} | Loppu={row[3]} | Kesto={row[4]} min")
    cursor.close()
    conn.close()

def nayta_kierrokset():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT sv.id, u.name, s.address, sv.start_time, sv.end_time,
               TIMESTAMPDIFF(MINUTE, sv.start_time, sv.end_time) AS kesto_min
        FROM site_visits sv
        JOIN users u ON sv.user_id = u.id
        JOIN sites s ON sv.site_id = s.id
        ORDER BY sv.start_time DESC
    """)
    print("\n--- Kierrokset ---")
    for row in cursor.fetchall():
        print(f"Kierros ID={row[0]} | Käyttäjä={row[1]} | Kohde={row[2]} | Alku={row[3]} | Loppu={row[4]} | Kesto={row[5]} min")
    cursor.close()
    conn.close()

def nayta_tyovuorot_ja_kierrokset():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ws.id AS session_id,
               u.name,
               ws.start_time AS vuoro_alku,
               ws.end_time AS vuoro_loppu,
               sv.id AS kierros_id,
               s.address,
               sv.start_time AS kierros_alku,
               sv.end_time AS kierros_loppu,
               TIMESTAMPDIFF(MINUTE, sv.start_time, sv.end_time) AS kierros_kesto
        FROM work_sessions ws
        JOIN users u ON ws.user_id = u.id
        LEFT JOIN site_visits sv ON sv.user_id = u.id 
            AND sv.start_time BETWEEN ws.start_time AND IFNULL(ws.end_time, NOW())
        LEFT JOIN sites s ON sv.site_id = s.id
        ORDER BY ws.start_time DESC, sv.start_time
    """)
    print("\n--- Työvuorot ja kierrokset ---")
    for row in cursor.fetchall():
        print(f"Vuoro {row[0]} ({row[1]}) {row[2]} - {row[3]} | Kierros {row[4]} | {row[5]} | {row[6]} - {row[7]} | {row[8]} min")
    cursor.close()
    conn.close()


# --- Menu ---
def menu():
    print("\n--- Työajanseuranta CLI ---")
    print("1. Aloita työvuoro")
    print("2. Lopeta työvuoro")
    print("3. Aloita kierros")
    print("4. Lopeta kierros")
    print("5. Lisää tapahtuma")
    print("6. Näytä työvuorot")
    print("7. Näytä kierrokset")
    print("8. Näytä työvuorot ja kierrokset")
    print("0. Lopeta")
if __name__ == "__main__":
    current_user = None

    while True:
        menu()
        choice = input("Valitse toiminto: ")

        if choice == "1":
            name = input("Anna käyttäjän nimi: ")
            password_hash = input("Anna salasana: ")
            user_id = hae_kayttaja(name, password_hash)
            if user_id:
                current_user = user_id
                aloita_tyovuoro(user_id)
            else:
                print(" Väärä nimi tai salasana.")

        elif choice == "2":
            if current_user:
                lopeta_tyovuoro(current_user)
            else:
                print(" Ei käyttäjää kirjautuneena.")

        elif choice == "3":
            if current_user:
                site_address = input("Anna kohteen osoite: ")
                aloita_kierros(current_user, site_address)
            else:
                print(" Aloita ensin työvuoro.")

        elif choice == "4":
            if current_user:
                lopeta_kierros(current_user)
            else:
                print(" Ei käyttäjää kirjautuneena.")

        elif choice == "5":
            if current_user:
                vid = int(input("Anna kierroksen ID: "))
                tyyppi = input("Tapahtuman tyyppi: ")
                kuvaus = input("Kuvaus: ")
                polku = input("Kuvan polku (tai tyhjä jos ei ole): ") or None
                lisaa_tapahtuma(vid, tyyppi, kuvaus, polku)
            else:
                print(" Ei käyttäjää kirjautuneena.")

        if choice == "6":
            nayta_tyovuorot()
        elif choice == "7":
            nayta_kierrokset()
        elif choice == "8":
            nayta_tyovuorot_ja_kierrokset()
        elif choice == "0":
            print("Ohjelma suljetaan.")
            break
        
        else:
            print(" Virheellinen valinta, yritä uudelleen.")
