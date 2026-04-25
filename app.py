from flask import Flask, render_template, redirect, request, session, flash
import mysql.connector
import os

app = Flask(__name__)
app.secret_key = "secret123"

# FUNCTION to connect to DB (fixes connection drop issue)
def get_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST") or "servicebridge-db.cvwme4im6tm5.us-east-2.rds.amazonaws.com",
        user=os.getenv("DB_USER") or "admin",
        password=os.getenv("DB_PASSWORD") or "edward14",
        database=os.getenv("DB_NAME") or "servicebridge_db"
    )

@app.route('/')
def home():
    return redirect('/login')

# LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = get_db()
        cursor = db.cursor()

        cursor.execute(
            "SELECT * FROM Users WHERE Username=%s AND Password=%s",
            (username, password)
        )
        user = cursor.fetchone()

        cursor.close()
        db.close()

        if user:
            session['user'] = username
            flash("Login successful!", "success")
            return redirect('/services')
        else:
            flash("Invalid username or password.", "error")

    return render_template('login.html')

# LOGOUT
@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("Logged out successfully.", "success")
    return redirect('/login')

# SERVICES
@app.route('/services')
def services():
    if 'user' not in session:
        return redirect('/login')

    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM Service")
    services = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM Booking")
    booking_count = cursor.fetchone()[0]

    cursor.close()
    db.close()

    return render_template(
        'services.html',
        services=services,
        booking_count=booking_count
    )

# BOOK
@app.route('/book/<int:service_id>')
def book(service_id):
    if 'user' not in session:
        return redirect('/login')

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "INSERT INTO Booking (ClientID, ServiceID, Status) VALUES (1, %s, 'Pending')",
        (service_id,)
    )

    db.commit()
    cursor.close()
    db.close()

    flash("Service booked successfully!", "success")
    return redirect('/services')

# BOOKINGS
@app.route('/bookings')
def bookings():
    if 'user' not in session:
        return redirect('/login')

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        SELECT Booking.BookingID, Service.Name, Booking.Status
        FROM Booking
        JOIN Service ON Booking.ServiceID = Service.ServiceID
    """)

    bookings = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template('bookings.html', bookings=bookings)

# COMPLETE BOOKING
@app.route('/update/<int:id>')
def update(id):
    if 'user' not in session:
        return redirect('/login')

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "UPDATE Booking SET Status='Completed' WHERE BookingID=%s",
        (id,)
    )

    db.commit()
    cursor.close()
    db.close()

    flash("Booking marked completed.", "success")
    return redirect('/bookings')

# DELETE BOOKING
@app.route('/delete/<int:id>')
def delete(id):
    if 'user' not in session:
        return redirect('/login')

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "DELETE FROM Booking WHERE BookingID=%s",
        (id,)
    )

    db.commit()
    cursor.close()
    db.close()

    flash("Booking deleted.", "success")
    return redirect('/bookings')

if __name__ == '__main__':
    app.run(debug=True)