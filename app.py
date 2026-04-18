from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)
DB_NAME = 'students.db'

# Database aur naya table initialize karne ka function
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Naya table 'students_full_data' banayenge jisme saare columns hain
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students_full_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            father_name TEXT NOT NULL,
            mother_name TEXT NOT NULL,
            dob TEXT NOT NULL,
            gender TEXT NOT NULL,
            mobile TEXT NOT NULL,
            email TEXT NOT NULL,
            course TEXT NOT NULL,
            roll_no TEXT NOT NULL,
            address TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Render/Gunicorn ke liye setup
with app.app_context():
    init_db()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        # Form se saara naya data collect karna
        name = request.form.get('name')
        father_name = request.form.get('father_name')
        mother_name = request.form.get('mother_name')
        dob = request.form.get('dob')
        gender = request.form.get('gender')
        mobile = request.form.get('mobile')
        email = request.form.get('email')
        course = request.form.get('course')
        roll_no = request.form.get('roll_no')
        address = request.form.get('address')

        try:
            # Data ko database mein insert karna
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO students_full_data 
                (name, father_name, mother_name, dob, gender, mobile, email, course, roll_no, address) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, father_name, mother_name, dob, gender, mobile, email, course, roll_no, address))
            conn.commit()
            conn.close()
            
            return f'''
                <div style="text-align:center; padding:50px; font-family:'Poppins', sans-serif; background:#f4f4f9; min-height:100vh;">
                    <h2 style="color: #28a745;">Registration Successful!</h2>
                    <p>Details for <b>{name}</b> have been successfully saved.</p>
                    <p style="color: #666;">We have recorded your Roll No: {roll_no} and Course: {course}</p>
                    <br>
                    <a href="/" style="padding:10px 20px; background:#71b7e6; color:white; text-decoration:none; border-radius:5px;">Fill Another Form</a>
                </div>
            '''
        except Exception as e:
            return f"Error details: {e}"

if __name__ == '__main__':
    app.run(debug=True)
        
