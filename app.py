from flask import Flask, render_template, request, redirect, flash
import mysql.connector
import os # Added to handle secret passwords safely

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'default_secret_for_local_testing')

# --- CLOUD DATABASE CONFIGURATION ---
# We use os.getenv to pull settings from Render's 'Environment' tab
db_config = {
    'host': os.getenv('DB_HOST', 'mysql80-victorvishal-database.i.aivencloud.com'),
    'user': os.getenv('DB_USER', 'avnadmin'),
    'password': os.getenv('DB_PASSWORD', 'AVNS_Wzhv4_NJjOsUXCi-Adq'), # Local fallback included
    'database': os.getenv('DB_NAME', 'defaultdb'),
    'port': int(os.getenv('DB_PORT', 23665))
}

def get_db():
    # Aiven requires SSL. ssl_verify_cert=False is common for free-tier cloud setups.
    return mysql.connector.connect(
        **db_config,
        ssl_disabled=False,
        ssl_verify_cert=False
    )

# --- HELPER FUNCTION FOR GRADES ---
def get_grade(percentage):
    if percentage >= 90: return "A+"
    elif percentage >= 80: return "A"
    elif percentage >= 70: return "B"
    elif percentage >= 60: return "C"
    elif percentage >= 50: return "D"
    elif percentage >= 40: return "E"
    else: return "F"

# --- ROUTES ---

@app.route('/')
def index():
    search_query = request.args.get('search', '')
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    sql = """
    SELECT s.student_id, s.student_name, s.roll_number, c.class_name,
           SUM(m.score) as total_score, 
           ROUND(AVG(m.score), 2) as percentage
    FROM students s
    LEFT JOIN classes c ON s.class_id = c.class_id
    LEFT JOIN marks m ON s.student_id = m.student_id
    """

    if search_query:
        sql += " WHERE s.student_name LIKE %s OR s.roll_number LIKE %s"
        sql += " GROUP BY s.student_id"
        cursor.execute(sql, (f"%{search_query}%", f"%{search_query}%"))
    else:
        sql += " GROUP BY s.student_id"
        cursor.execute(sql)

    students = cursor.fetchall()
    cursor.execute("SELECT * FROM classes")
    classes = cursor.fetchall()
    cursor.execute("SELECT * FROM subjects")
    subjects = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template('index.html', students=students, classes=classes, subjects=subjects)

@app.route('/add', methods=['POST'])
def add():
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO students (student_name, roll_number, class_id) VALUES (%s, %s, %s)",
                       (request.form['name'], request.form['roll'], request.form['class_id']))
        s_id = cursor.lastrowid
        subject_ids = request.form.getlist('subject_id[]')
        scores = request.form.getlist('score[]')
        for sub_id, score in zip(subject_ids, scores):
            if score:
                cursor.execute("INSERT INTO marks (student_id, subject_id, score) VALUES (%s, %s, %s)",
                               (s_id, sub_id, score))
        conn.commit()
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
    return redirect('/')

@app.route('/edit/<int:id>')
def edit_page(id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students WHERE student_id = %s", (id,))
    student = cursor.fetchone()
    cursor.execute("SELECT * FROM classes")
    classes = cursor.fetchall()
    cursor.execute("""
        SELECT s.subject_id, s.subject_name, m.score 
        FROM subjects s
        LEFT JOIN marks m ON s.subject_id = m.subject_id AND m.student_id = %s
    """, (id,))
    marks = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('edit.html', student=student, classes=classes, marks=marks)

@app.route('/update/<int:id>', methods=['POST'])
def update(id):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE students SET student_name=%s, roll_number=%s, class_id=%s WHERE student_id=%s",
                       (request.form['name'], request.form['roll'], request.form['class_id'], id))
        cursor.execute("DELETE FROM marks WHERE student_id = %s", (id,))
        subject_ids = request.form.getlist('subject_id[]')
        scores = request.form.getlist('score[]')
        for sub_id, score in zip(subject_ids, scores):
            if score:
                cursor.execute("INSERT INTO marks (student_id, subject_id, score) VALUES (%s, %s, %s)",
                               (id, sub_id, score))
        conn.commit()
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
    return redirect('/')

@app.route('/delete/<int:id>')
def delete(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE student_id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect('/')

@app.route('/marksheet/<int:id>')
def marksheet(id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT s.*, c.class_name FROM students s LEFT JOIN classes c ON s.class_id = c.class_id WHERE s.student_id = %s", (id,))
    student = cursor.fetchone()
    cursor.execute("SELECT sub.subject_name, m.score FROM marks m JOIN subjects sub ON m.subject_id = sub.subject_id WHERE m.student_id = %s", (id,))
    marks = cursor.fetchall()
    total_score = sum(item['score'] for item in marks) if marks else 0
    count = len(marks) if marks else 1
    avg_percentage = total_score / count
    final_grade = get_grade(avg_percentage)
    cursor.close()
    conn.close()
    return render_template('marksheet.html', student=student, marks=marks, total=total_score, percentage=round(avg_percentage, 2), grade=final_grade)

if __name__ == '__main__':
    app.run(debug=True)