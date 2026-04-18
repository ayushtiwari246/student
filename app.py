from flask import Flask, render_template, request, jsonify, session
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename
import sqlite3
import random
import os

app = Flask(__name__)
app.secret_key = 'ayushi_student_portal_key'

# --- IMAGE UPLOAD SETTINGS ---
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Agar static/uploads folder nahi hai, toh app start hote hi ban jayega
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- EMAIL CONFIGURATION ---
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'Ayushtiwari02929@gmail.com' 
app.config['MAIL_PASSWORD'] = 'ewwzrcjkyzjehvge' 
mail = Mail(app)

DB_NAME = 'students.db'

# Database Setup (Naya table images ke column ke sath)
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS students_with_images (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        first_name TEXT, last_name TEXT, father_name TEXT, 
        mother_name TEXT, dob TEXT, email TEXT, mobile TEXT, 
        course TEXT, roll_no TEXT, address TEXT,
        photo_path TEXT, signature_path TEXT)''')
    conn.commit()
    conn.close()

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
        msg = Message('Student Portal - Verification Code', 
                      sender=app.config['MAIL_USERNAME'], 
                      recipients=[email])
        msg.body = f"Aapka Registration OTP code hai: {otp}\nKripya ise form mein enter karein."
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

# Submit Route with File Upload and Print Slip
@app.route('/submit', methods=['POST'])
def submit():
    if not session.get('is_verified'):
        return "Error: Pehle Email Verify karein!"
    
    # Form data nikalna
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    father_name = request.form.get('father_name')
    mother_name = request.form.get('mother_name')
    dob = request.form.get('dob')
    email = request.form.get('email')
    mobile = request.form.get('mobile')
    course = request.form.get('course')
    roll_no = request.form.get('roll_no')
    address = request.form.get('address')
    
    # --- FILE UPLOAD LOGIC ---
    photo_file = request.files.get('photo')
    signature_file = request.files.get('signature')

    # Images ko roll number ke naam se save karna (e.g. 101_photo.jpg)
    photo_ext = photo_file.filename.split('.')[-1]
    sig_ext = signature_file.filename.split('.')[-1]
    
    photo_filename = secure_filename(f"{roll_no}_photo.{photo_ext}")
    sig_filename = secure_filename(f"{roll_no}_sig.{sig_ext}")
    
    photo_path = os.path.join(app.config['UPLOAD_FOLDER'], photo_filename)
    sig_path = os.path.join(app.config['UPLOAD_FOLDER'], sig_filename)
    
    photo_file.save(photo_path)
    signature_file.save(sig_path)

    # Database mein saara data + images ka rasta (path) save karna
    data = (first_name, last_name, father_name, mother_name, dob, email, mobile, course, roll_no, address, photo_path, sig_path)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO students_with_images 
                   (first_name, last_name, father_name, mother_name, dob, email, mobile, course, roll_no, address, photo_path, signature_path) 
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''', data)
    conn.commit()
    application_no = cursor.lastrowid 
    conn.close()
    
    session.pop('is_verified', None)
    
    # --- PRINT SLIP GENERATION ---
    return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Admission Acknowledgment</title>
            <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap" rel="stylesheet">
            <style>
                body {{ font-family: 'Poppins', sans-serif; background: #f4f4f9; padding: 20px; }}
                .print-container {{ background: white; max-width: 800px; margin: 0 auto; padding: 40px; border: 2px solid #333; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); position: relative; }}
                .header {{ text-align: center; border-bottom: 2px solid #333; padding-bottom: 15px; margin-bottom: 20px; }}
                .header h2 {{ margin: 0; color: #2c3e50; text-transform: uppercase; font-size: 22px; }}
                .content-wrapper {{ display: flex; gap: 20px; }}
                .details-table {{ flex: 3; width: 100%; border-collapse: collapse; }}
                .details-table th, .details-table td {{ border: 1px solid #ccc; padding: 10px; text-align: left; font-size: 14px; }}
                .details-table th {{ background-color: #f8f9fa; width: 35%; }}
                .images-box {{ flex: 1; text-align: center; border: 1px solid #ccc; padding: 10px; background: #f8f9fa; }}
                .images-box img {{ max-width: 130px; border: 1px solid #999; margin-bottom: 5px; }}
                .sig-img {{ height: 40px; object-fit: contain; }}
                .btn-container {{ text-align: center; margin-top: 30px; }}
                .print-btn {{ background: #28a745; color: white; border: none; padding: 10px 25px; font-size: 16px; cursor: pointer; border-radius: 5px; margin-right: 10px; }}
                .home-btn {{ background: #9b59b6; color: white; border: none; padding: 10px 25px; font-size: 16px; cursor: pointer; border-radius: 5px; text-decoration: none; }}
                @media print {{
                    .btn-container {{ display: none; }}
                    body {{ background: white; }}
                    .print-container {{ border: none; box-shadow: none; padding: 0; }}
                }}
            </style>
        </head>
        <body>
            <div class="print-container">
                <div class="header">
                    <h2>Official Admission Acknowledgment Slip</h2>
                    <p style="margin-top: 5px;">Application No: <b>APP-2026-{application_no}</b></p>
                </div>
                
                <div class="content-wrapper">
                    <table class="details-table">
                        <tr><th>Full Name</th><td>{first_name} {last_name}</td></tr>
                        <tr><th>Father's Name</th><td>{father_name}</td></tr>
                        <tr><th>Mother's Name</th><td>{mother_name}</td></tr>
                        <tr><th>Date of Birth</th><td>{dob}</td></tr>
                        <tr><th>Course Enrolled</th><td>{course}</td></tr>
                        <tr><th>Roll Number</th><td>{roll_no}</td></tr>
                        <tr><th>Email ID</th><td>{email}</td></tr>
                        <tr><th>Mobile No.</th><td>{mobile}</td></tr>
                        <tr><th>Address</th><td>{address}</td></tr>
                    </table>

                    <div class="images-box">
                        <p style="font-size: 12px; font-weight: bold; margin-bottom:5px;">Applicant Photo</p>
                        <img src="/{photo_path}" alt="Applicant Photo">
                        
                        <p style="font-size: 12px; font-weight: bold; margin-top:15px; margin-bottom:5px;">Signature</p>
                        <img src="/{sig_path}" alt="Signature" class="sig-img">
                    </div>
                </div>

                <div class="header" style="border-top: 2px solid #333; border-bottom: none; padding-top: 10px; margin-top:30px;">
                    <p style="font-size: 12px;"><i>This is a computer-generated slip. Please preserve it for future reference.</i></p>
                </div>

                <div class="btn-container">
                    <button class="print-btn" onclick="window.print()">🖨️ Print Slip</button>
                    <a href="/" class="home-btn">Go Back</a>
                </div>
            </div>
        </body>
        </html>
    '''

if __name__ == '__main__':
    app.run(debug=True)
    
