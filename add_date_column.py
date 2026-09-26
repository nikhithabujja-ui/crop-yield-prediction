import sqlite3

conn = sqlite3.connect("crop_yield.db")

cursor = conn.cursor()

try:

    cursor.execute("""
        ALTER TABLE predictions
        ADD COLUMN prediction_date TEXT
    """)

    conn.commit()

    print("Prediction date column added successfully!")

except sqlite3.OperationalError:

    print("Prediction date column already exists.")

conn.close()