from flask import Flask, render_template, redirect
import mysql.connector

app = Flask(__name__)

# CONNECT TO DATABASE
db = mysql.connector.connect(
    host="servicebridge-db.cvwme4im6tm5.us-east-2.rds.amazonaws.com",
    user="admin",
    password="edward14",
    database="servicebridge_db"
)


cursor = db.cursor()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/services')
def services():
    cursor.execute("SELECT * FROM Service")
    data = cursor.fetchall()
    return render_template('services.html', services=data)

@app.route('/book/<int:service_id>')
def book(service_id):
    cursor.execute(
        "INSERT INTO Booking (ClientID, ServiceID, Status) VALUES (1, %s, 'Pending')",
        (service_id,)
    )
    db.commit()
    return redirect('/services')

@app.route('/bookings')
def view_bookings():
    cursor.execute("SELECT * FROM Booking")
    data = cursor.fetchall()
    return render_template('bookings.html', bookings=data)


@app.route('/update/<int:id>')
def update(id):
    cursor.execute(
        "UPDATE Booking SET Status='Completed' WHERE BookingID=%s",
        (id,)
    )
    db.commit()
    return redirect('/bookings')

@app.route('/delete/<int:id>')
def delete(id):
    cursor.execute(
        "DELETE FROM Booking WHERE BookingID=%s",
        (id,)
    )
    db.commit()
    return redirect('/bookings')

if __name__ == '__main__':
    app.run(debug=True)