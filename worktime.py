import mysql.connector

# Yhteys tietokantaan
conn = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="test",
    database="work_tracking"
)

cursor = conn.cursor()

# Testi — haetaan käyttäjät
cursor.execute("SELECT * FROM users")
for row in cursor.fetchall():
    print(row)

cursor.close()
conn.close()

import mysql.connector

conn = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="test",
    database="work_tracking"
)

cursor = conn.cursor()

sql = "INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)"
values = ("Matti Meikäläinen", "matti@example.com", "salasanan_hash")
cursor.execute(sql, values)

conn.commit()

print(f"{cursor.rowcount} käyttäjä lisätty.")

cursor.close()
conn.close()
