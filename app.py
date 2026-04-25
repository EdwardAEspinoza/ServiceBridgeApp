from flask import Flask, render_template, redirect, request, session
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

# HOME → redirect to login
@app.route('/')
def home():
    return redirect('/login')

# LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None

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
            return redirect('/services')
        else:
            error = "Invalid username or password"

    return render_template('login.html', error=error)

# LOGOUT
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

# VIEW SERVICES
@app.route('/services')
def services():
    if 'user' not in session:
        return redirect('/login')

    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM Service")
    data = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template('services.html', services=data)

# BOOK SERVICE
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

    return redirect('/services')

# VIEW BOOKINGS
@app.route('/bookings')
def view_bookings():
    if 'user' not in session:
        return redirect('/login')

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

    return redirect('/bookings')

if __name__ == '__main__':
    app.run(debug=True)