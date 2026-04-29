import os
import sqlite3
import tempfile
import unittest

import app as flights_app


class FlaskFlightsTests(unittest.TestCase):

    def setUp(self):
        fd, self.database_path = tempfile.mkstemp()
        os.close(fd)

        flights_app.app.config["TESTING"] = True
        flights_app.DATABASE = self.database_path

        self.client = flights_app.app.test_client()

        connection = sqlite3.connect(flights_app.DATABASE)
        cursor = connection.cursor()

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

        cursor.execute("""
        INSERT INTO flights (origin, destination, departure_time, arrival_time)
        VALUES (?, ?, ?, ?)
        """, ("Atlanta", "New York", "2026-05-01 08:00", "2026-05-01 10:15"))

        cursor.execute("""
        INSERT INTO passengers (name, flight_id)
        VALUES (?, ?)
        """, ("Alice", 1))

        connection.commit()
        connection.close()

    def tearDown(self):
        if os.path.exists(self.database_path):
            os.unlink(self.database_path)

    def test_index_page_loads(self):
        """Homepage should load and show the list of flights."""
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Flights", response.data)
        self.assertIn(b"Atlanta to New York", response.data)

    def test_flight_detail_page_loads(self):
        """Flight detail page should show flight information."""
        response = self.client.get("/flights/1")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Atlanta to New York", response.data)
        self.assertIn(b"Alice", response.data)

    def test_invalid_flight_returns_404(self):
        """A missing flight should return 404."""
        response = self.client.get("/flights/999")

        self.assertEqual(response.status_code, 404)
        self.assertIn(b"Flight not found", response.data)

    def test_origin_and_destination_cannot_match(self):
        """A flight cannot have the same origin and destination."""
        response = self.client.post("/flights/add", data={
            "origin": "Atlanta",
            "destination": "Atlanta",
            "departure_time": "2026-05-01 08:00",
            "arrival_time": "2026-05-01 10:00"
        })

        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Invalid time or Origin/Destination", response.data)

    def test_departure_must_be_before_arrival(self):
        """Departure time must be before arrival time."""
        response = self.client.post("/flights/add", data={
            "origin": "Atlanta",
            "destination": "Miami",
            "departure_time": "2026-05-01 12:00",
            "arrival_time": "2026-05-01 10:00"
        })

        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Invalid time or Origin/Destination", response.data)

    def test_add_valid_flight(self):
        """A valid flight should be added successfully."""
        response = self.client.post(
            "/flights/add",
            data={
                "origin": "Boston",
                "destination": "Chicago",
                "departure_time": "2026-05-02 09:00",
                "arrival_time": "2026-05-02 11:30"
            },
            follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Boston to Chicago", response.data)

    def test_book_passenger(self):
        """A passenger should be added to an existing flight."""
        response = self.client.post(
            "/flights/1/book",
            data={"passenger": "Bob"},
            follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Bob", response.data)


if __name__ == "__main__":
    unittest.main(verbosity=1)