from flask import Flask, render_template, redirect
import mysql.connector
import os

app = Flask(__name__)

# FUNCTION to connect to DB (fixes connection drop issue)
def get_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST") or "servicebridge-db.cvwme4im6tm5.us-east-2.rds.amazonaws.com",
        user=os.getenv("DB_USER") or "admin",
        password=os.getenv("DB_PASSWORD") or "edward14",
        database=os.getenv("DB_NAME") or "servicebridge_db"
    )

# HOME PAGE
@app.route('/')
def home():
    return render_template('index.html')

# VIEW SERVICES
@app.route('/services')
def services():
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM Service")
    data = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template('services.html', services=data)

# BOOK SERVICE (INSERT)
@app.route('/book/<int:service_id>')
def book(service_id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "INSERT INTO Booking (ClientID, ServiceID, Status) VALUES (1, %s, 'Pending')",
        (service_id,)
    )
    db.commit()

    cursor.close()
    db.close()

    return redirect('/services')

# VIEW BOOKINGS
@app.route('/bookings')
def view_bookings():
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM Booking")
    data = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template('bookings.html', bookings=data)

# UPDATE BOOKING
@app.route('/update/<int:id>')
def update(id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "UPDATE Booking SET Status='Completed' WHERE BookingID=%s",
        (id,)
    )
    db.commit()

    cursor.close()
    db.close()

    return redirect('/bookings')

# DELETE BOOKING
@app.route('/delete/<int:id>')
def delete(id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "DELETE FROM Booking WHERE BookingID=%s",
        (id,)
    )
    db.commit()

    cursor.close()
    db.close()

    return redirect('/bookings')

if __name__ == '__main__':
    app.run(debug=True)