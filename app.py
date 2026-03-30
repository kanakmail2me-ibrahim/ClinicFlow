import os
import psycopg2
from flask import Flask, render_template, request, redirect, session, url_for
from config import DOCTOR_DATA
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# Database se connect karne ka function
def get_db_connection():
    conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
    return conn

app.secret_key = "secret_clinic_key" # Session ko secure karne ke liye

@app.route("/")
def home():
    return render_template("index.html", data=DOCTOR_DATA)

# Ye naya route hai data save karne ke liye
@app.route("/book", methods=["POST"])
def book_appointment():
    # Form se data nikalna
    name = request.form.get("name")
    phone = request.form.get("phone")
    age = request.form.get("age")
    date = request.form.get("date")
    msg = request.form.get("message")
    
    # Database mein likhna (Insert)
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO appointments (patient_name, phone, appt_date, message) VALUES (%s, %s, %s, %s)",
                (name, phone, date, msg))
    conn.commit() # Changes save karein
    cur.close()
    conn.close()
    
    return "<h1>Shukriya! Aapka appointment book ho gaya hai.</h1><a href='/'>Wapas jayein</a>"

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_pass = request.form.get("password")
        if user_pass == os.environ.get("ADMIN_PASSWORD", "doctor@123"):
            session['logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return "Wrong Password! <a href='/login'>Try Again</a>"
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route("/admin")
def admin_dashboard():
    # Pehle check karo ki doctor login hai ya nahi
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cur = conn.cursor()
    # Saare appointments ko naye se purane (DESC) order mein mangwao
    cur.execute("SELECT id, patient_name, phone, appt_date, message FROM appointments ORDER BY id DESC")
    appointments = cur.fetchall()
    cur.close()
    conn.close()
    
    return render_template("admin.html", data=appointments)

# Purana appointment delete karne ka rasta
@app.route("/delete/<int:id>")
def delete_appointment(id):
    if not session.get('logged_in'): return redirect(url_for('login'))
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM appointments WHERE id = %s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('admin_dashboard'))

if __name__ == "__main__":
    app.run(debug=True)