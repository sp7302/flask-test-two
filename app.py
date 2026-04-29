import sqlite3
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

DATABASE = "flights.db"


def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def valid_flight(origin, destination, departure_time, arrival_time):
    departure = datetime.strptime(departure_time, "%Y-%m-%d %H:%M")
    arrival = datetime.strptime(arrival_time, "%Y-%m-%d %H:%M")
    if departure < arrival or origin != destination:
        return True, ""
    return False, "Invalid time or Origin/Destination"

    
@app.route("/")
def index():
    connection = get_connection()
    flights = connection.execute("""
        SELECT * FROM flights
        ORDER BY departure_time
    """).fetchall()
    connection.close()

    return render_template("index.html", flights=flights)


@app.route("/flights/<int:flight_id>")
def flight_detail(flight_id):
    connection = get_connection()

    flight = connection.execute(
        """
        SELECT * FROM flights
        WHERE id = ?
    """,
        (flight_id,),
    ).fetchone()

    if flight is None:
        connection.close()
        return render_template("flight.html", flight=None), 404

    passengers = connection.execute(
        """
        SELECT * FROM passengers
        WHERE flight_id = ?
        ORDER BY name
    """,
        (flight_id,),
    ).fetchall()

    connection.close()

    return render_template("flight.html", flight=flight, passengers=passengers)


@app.route("/flights/add", methods=["GET", "POST"])
def add_flight():
    if request.method == "POST":
        origin = request.form.get("origin", "").strip()
        destination = request.form.get("destination", "").strip()
        departure_time = request.form.get("departure_time", "").strip()
        arrival_time = request.form.get("arrival_time", "").strip()

        is_valid, message = valid_flight(
            origin, destination, departure_time, arrival_time
        )

        if not is_valid:
            return render_template("add_flight.html", message=message), 400

        connection = get_connection()
        connection.execute(
            """
            INSERT INTO flights (origin, destination, departure_time, arrival_time)
            VALUES (?, ?, ?, ?)
        """,
            (origin, destination, departure_time, arrival_time),
        )
        connection.commit()
        connection.close()

        return redirect(url_for("index"))

    return render_template("add_flight.html")


@app.route("/flights/<int:flight_id>/book", methods=["POST"])
def book(flight_id):
    passenger = request.form.get("passenger", "").strip()

    if not passenger:
        return "Passenger name is required.", 400

    connection = get_connection()

    flight = connection.execute(
        """
        SELECT * FROM flights
        WHERE id = ?
    """,
        (flight_id,),
    ).fetchone()

    if flight is None:
        connection.close()
        return "Flight not found.", 404

    connection.execute(
        """
        INSERT INTO passengers (name, flight_id)
        VALUES (?, ?)
    """,
        (passenger, flight_id),
    )

    connection.commit()
    connection.close()

    return redirect(url_for("flight_detail", flight_id=flight_id))


if __name__ == "__main__":
    app.run(debug=True)
