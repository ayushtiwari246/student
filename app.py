from flask import Flask, render_template, request, jsonify, session
from flask_mail import Mail, Message
import sqlite3
import random
import os

app = Flask(__name__)
app.secret_key = 'ayushi_student_portal_key' # Session ke liye secret key

# --- EMAIL CONFIGURATION (Final) ---
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True

# YAHAN APNI GMAIL ID DAALEIN (Line 14)
app.config['MAIL_USERNAME'] = 'aapki-email-yaha-likhiye@gmail.com' 

# Aapka naya App Password (bina space ke)
app.config['MAIL_PASSWORD'] = 'ewwzrcjkyzjehvge' 
mail = Mail(app)

DB_NAME = 'students.db'

# Database Setup
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS verified_students (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, father_name TEXT, 
        mother_name TEXT, dob TEXT, email TEXT, mobile TEXT, 
        course TEXT, roll_no TEXT, address TEXT)''')
    conn.commit()
    conn.close()

# Render Startup ke waqt DB banana
with app.app_context():
    init_db()

@app.route('/')
def home():
    return render_template('index.html')

# OTP Bhejne ka Route
@app.route('/send_otp', methods=['POST'])
def send_otp():
    email = request.form.get('email')
    otp = str(random.randint(100000, 999999))
    session['current_otp'] = otp
    try:
        msg = Message('Student Portal - Verification Code', 
                      sender=app.config['MAIL_USERNAME'], 
                      recipients=[email])
        msg.body = f"Aapka Registration OTP code hai: {otp}\nKripya ise form mein enter karein taaki form submit ho sake."
        mail.send(msg)
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

# OTP Check karne ka Route
@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    if request.form.get('otp') == session.get('current_otp'):
        session['is_verified'] = True
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error'})

# Final Data Save karne ka Route
@app.route('/submit', methods=['POST'])
def submit():
    if not session.get('is_verified'):
        return "Error: Pehle Email Verify karein!"
    
    data = (
        request.form.get('name'), request.form.get('father_name'),
        request.form.get('mother_name'), request.form.get('dob'),
        request.form.get('email'), request.form.get('mobile'),
        request.form.get('course'), request.form.get('roll_no'),
        request.form.get('address')
    )

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO verified_students 
                   (name, father_name, mother_name, dob, email, mobile, course, roll_no, address) 
                   VALUES (?,?,?,?,?,?,?,?,?)''', data)
    conn.commit()
    conn.close()
    
    session.pop('is_verified', None) # Security ke liye verification clear karein
    
    return f'''
        <div style="text-align:center; padding:50px; font-family:sans-serif; background:#f4f4f9; min-height:100vh;">
            <h2 style="color: #28a745;">Form Submitted Successfully!</h2>
            <p>Badhai ho <b>{request.form.get('name')}</b>, aapka verified data save ho gaya hai.</p>
            <br>
            <a href="/" style="padding:10px 20px; background:#9b59b6; color:white; text-decoration:none; border-radius:5px;">Wapas Jayein</a>
        </div>
    '''

if __name__ == '__main__':
    app.run(debug=True)
