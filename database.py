import sqlite3

conn = sqlite3.connect("crop_yield.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    crop TEXT,
    rainfall REAL,
    temperature REAL,
    humidity REAL,
    soil_ph REAL,
    nitrogen REAL,
    phosphorus REAL,
    potassium REAL,
    predicted_yield REAL
)
""")

conn.commit()
conn.close()

print("Database created successfully!")