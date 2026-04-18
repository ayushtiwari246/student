from flask import Flask, render_template, request, jsonify, session
from flask_mail import Mail, Message
import sqlite3
import random
import os

app = Flask(__name__)
app.secret_key = 'ayushi_mgkvp_key' # Secret key for sessions

# --- EMAIL CONFIGURATION ---
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'tumhari-email@gmail.com' # <--- APNI GMAIL LIKHEIN
app.config['MAIL_PASSWORD'] = 'xxxx xxxx xxxx xxxx' # <--- GMAIL APP PASSWORD
mail = Mail(app)

DB_NAME = 'students.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS verified_students (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, father_name TEXT, 
        mother_name TEXT, dob TEXT, email TEXT, mobile TEXT, 
        course TEXT, roll_no TEXT, address TEXT)''')
    conn.commit()
    conn.close()

# Render startup
with app.app_context():
    init_db()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/send_otp', methods=['POST'])
def send_otp():
    email = request.form.get('email')
    otp = str(random.randint(100000, 999999))
    session['current_otp'] = otp
    try:
        msg = Message('Student Portal - Verification Code', sender=app.config['MAIL_USERNAME'], recipients=[email])
        msg.body = f"Aapka registration OTP code hai: {otp}\nKripya ise form mein enter karein."
        mail.send(msg)
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    if request.form.get('otp') == session.get('current_otp'):
        session['is_verified'] = True
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error'})

@app.route('/submit', methods=['POST'])
def submit():
    if not session.get('is_verified'):
        return "Pehle Email Verify karein!"
    
    data = (
        request.form.get('name'), request.form.get('father_name'),
        request.form.get('mother_name'), request.form.get('dob'),
        request.form.get('email'), request.form.get('mobile'),
        request.form.get('course'), request.form.get('roll_no'),
        request.form.get('address')
    )

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO verified_students (name, father_name, mother_name, dob, email, mobile, course, roll_no, address) VALUES (?,?,?,?,?,?,?,?,?)', data)
    conn.commit()
    conn.close()
    
    session.pop('is_verified', None) # Reset verification
    return f"<h2>Badhai ho! {request.form.get('name')} ka form submit ho gaya hai.</h2><a href='/'>Wapas Jayein</a>"

if __name__ == '__main__':
    app.run(debug=True)
    
