import sqlite3

connection = sqlite3.connect("flights.db")
cursor = connection.cursor()

cursor.execute("DROP TABLE IF EXISTS passengers")
cursor.execute("DROP TABLE IF EXISTS flights")

cursor.execute("""
CREATE TABLE flights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    origin TEXT NOT NULL,
    destination TEXT NOT NULL,
    departure_time TEXT NOT NULL,
    arrival_time TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE passengers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    flight_id INTEGER NOT NULL,
    FOREIGN KEY (flight_id) REFERENCES flights(id)
)
""")

flights = [
    ("Atlanta", "New York", "2026-05-01 08:00", "2026-05-01 10:15"),
    ("Atlanta", "Miami", "2026-05-01 12:30", "2026-05-01 14:10"),
    ("Paris", "Tokyo", "2026-05-02 09:00", "2026-05-03 06:30"),
]

cursor.executemany(
    """
INSERT INTO flights (origin, destination, departure_time, arrival_time)
VALUES (?, ?, ?, ?)
""",
    flights,
)

passengers = [
    ("Alice", 1),
    ("Bob", 1),
    ("Charlie", 2),
]

cursor.executemany(
    """
INSERT INTO passengers (name, flight_id)
VALUES (?, ?)
""",
    passengers,
)

connection.commit()
connection.close()

print("Database initialized.")
