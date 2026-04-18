from flask import Flask, render_template, request
import sqlite3
import os

app = Flask(__name__)

# Database file ka naam
DB_NAME = 'students.db'

# Database initialize karne ka function
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Table banayenge agar nahi hai toh
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS student_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll_no TEXT NOT NULL,
            course TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Render par startup ke waqt database banane ke liye
with app.app_context():
    init_db()

@app.route('/')
def home():
    # templates/index.html ko render karega
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        # Form se data uthana
        name = request.form.get('name')
        roll_no = request.form.get('roll_no')
        course = request.form.get('course')

        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO student_data (name, roll_no, course) 
                VALUES (?, ?, ?)
            ''', (name, roll_no, course))
            conn.commit()
            conn.close()
            
            # Registration success message
            return f'''
                <div style="text-align:center; padding:50px; font-family:'Poppins', sans-serif; background:#f4f4f9; min-height:100vh;">
                    <h2 style="color: #9b59b6;">Registration Successful!</h2>
                    <p>Shukriya <b>{name}</b>, aapki details save ho gayi hain.</p>
                    <br>
                    <a href="/" style="padding:10px 20px; background:#71b7e6; color:white; text-decoration:none; border-radius:5px;">Wapas Jayein</a>
                </div>
            '''
        except Exception as e:
            return f"Kuch error aaya: {e}"

if __name__ == '__main__':
    # Local machine par testing ke liye
    app.run(debug=True)
            
