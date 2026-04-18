from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Database initialize karne ka function
def init_db():
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    # Table banayenge agar pehle se nahi hai
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

# Home page route - Yahan aapka professional HTML form dikhega
@app.route('/')
def home():
    return render_template('index.html')

# Form submission route - Yahan data process hoga
@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        # Form fields se data nikalna
        name = request.form.get('name')
        roll_no = request.form.get('roll_no')
        course = request.form.get('course')

        try:
            # Database mein data insert karna
            conn = sqlite3.connect('students.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO student_data (name, roll_no, course) 
                VALUES (?, ?, ?)
            ''', (name, roll_no, course))
            conn.commit()
            conn.close()
            
            # Success message ya redirect
            return f'''
                <div style="text-align:center; padding:50px; font-family:sans-serif;">
                    <h2 style="color: #28a745;">Registration Successful!</h2>
                    <p>Thank you <b>{name}</b>, your details have been saved.</p>
                    <a href="/" style="text-decoration:none; color:#9b59b6;">Go Back to Form</a>
                </div>
            '''
        except Exception as e:
            return f"Error occurred: {e}"

if __name__ == '__main__':
    init_db()  # Server start hote hi database setup ho jayega
    app.run(debug=True)
