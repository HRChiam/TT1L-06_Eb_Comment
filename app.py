import os
from flask import Flask, render_template, request, redirect, url_for, session
from wtforms import StringField, SubmitField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from models import db, Users, Lecturer
import sqlite3
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, instance_relative_config=True)

# Ensure the instance folder exists
if not os.path.exists(app.instance_path):
    os.makedirs(app.instance_path)

DATABASE_NAME = "database.db"
DATABASE_PATH = os.path.join(app.instance_path, DATABASE_NAME)

app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DATABASE_PATH}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_secret_key')

db.init_app(app)

def get_db_connection():
    con = sqlite3.connect(DATABASE_PATH)
    con.row_factory = sqlite3.Row
    return con

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login')
def login():       
    return render_template('login.html')

@app.route('/signin')
def signin():
    return render_template('signin.html')

@app.route('/forgot')
def forgot():
    return render_template('forgot.html')

@app.route('/process_signin', methods=['POST'])
def process_signin():
    if request.method == 'POST':
        name = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        error= {}

        if email.endswith('@student.mmu.edu.my') and len(email.split('@')[0]) == 10:
            pass
        elif email.endswith('@mmu.edu.my'):
            pass
        else:
            error['email'] = "Email invalid or does not meet requirements"

        if not (len(password) >= 8 and sum(c.isdigit() for c in password) >= 4) or password != confirm_password:
            error['password'] = "Password does not match or does not meet requirements"

        if not error:
            con = get_db_connection()
            cur = con.cursor()

            cur.execute(
                "INSERT INTO users(name, email, password) VALUES (?, ?, ?)",
                (name, email, password)
            )

            con.commit()
            con.close()


            if email.endswith('@student.mmu.edu.my'):
                return redirect('/front')
            elif email.endswith('@mmu.edu.my'):
                return redirect('/admin')

        return render_template('signin.html', error=error)

    return render_template('signin.html')


@app.route('/process_login', methods=['GET', 'POST'])
def process_login():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

     
        student_email = email.endswith('@student.mmu.edu.my')and len(email.split('@')[0]) == 10

        if student_email:
            return redirect('/front') 
        

        elif email.endswith('@mmu.edu.my'):
            return redirect('/index')
        

        elif username == "admin" and email == "admin@gmail.com" and password == "123":
            session["logged_in"] = True
            return redirect ("/admin")

        else:
            error_message = "Email invalid or does not meet requirements"
            return render_template('login.html', error=error_message)


    return render_template('login.html')


@app.route('/front')
def studentfront():
    return render_template('studentfront.html')

@app.route('/main')
def studentmain():
    return render_template('studentmain.html')

@app.route('/FCI')
def FCI():
    return render_template('Cyber_FCI_lecturer.html')

@app.route('/FCM')
def FCM():
    return render_template('Cyber_FCM_lecturer.html')

@app.route('/FCA')
def FCA():
    return render_template('Cyber_FCA_lecturer.html')

@app.route('/FAC')
def FAC():
    return render_template('Cyber_FAC_lecturer.html')

@app.route('/FOM')
def FOM():
    return render_template('Cyber_FOM_lecturer.html')

@app.route('/FOE')
def FOE():
    return render_template('Cyber_FOE_lecturer.html')

@app.route('/FET')
def FET():
    return render_template('Melaka_FET_lecturer.html')

@app.route('/FIST')
def FIST():
    return render_template('Melaka_FIST_lecturer.html')

@app.route('/FOL')
def FOL():
    return render_template('Melaka_FOL_lecturer.html')

@app.route('/FOB')
def FOB():
    return render_template('Melaka_FOB_lecturer.html')

@app.route('/keyin')
def keyin():
    return render_template('keyin.html')

@app.route('/upload', methods=['POST'])
def upload():
    name = request.form['name']
    photo = request.files['photo']
    phone = request.form['phone']
    email = request.form['email']
    campus = request.form['campus']
    faculty = request.form['faculty']

    if not os.path.exists('uploads'):
        os.makedirs('uploads')

    photo.save(os.path.join('uploads/' + photo.filename))

    lecturer = Lecturer(name=name, photo=photo.filename, phone=phone, email=email, campus=campus, faculty=faculty)
    db.session.add(lecturer)
    db.session.commit()

    return redirect(url_for('keyinsuccess'))

@app.route('/keyinsuccess')
def keyinsuccess():
    return render_template('keyinsuccess.html')

@app.route("/admin")
def admin():
    con = get_db_connection()
    cursor = con.cursor()

    cursor.execute("SELECT COUNT(*) FROM lecturer ")
    num_lecturers = cursor.fetchone()[0]  # Fetch the first result
    cursor.execute("SELECT COUNT(*) FROM users ")  # Execute a new query
    num_users = cursor.fetchone()[0]  # Fetch the first result from the new query
    cursor.execute("SELECT COUNT(*) FROM comment ")  # Execute a new query
    num_comment = cursor.fetchone()[0]  # Fetch the first result from the new query
    
    return render_template("admin.html", num_lecturers=num_lecturers, num_users=num_users, num_comment=num_comment)


@app.route("/user")
def usercontrol():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    user_data = cursor.fetchall()
    conn.close()

    return render_template("admin_user.html", users=user_data)

def delete_user(name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE name=?", (name,))
    conn.commit()
    conn.close()


@app.route('/delete_user', methods=["POST"])
def delete_user_route():
    name = request.form['name']
    delete_user(name)
    return redirect('/user')

def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@app.route("/admin_comment")
def comment():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM comment")
    comment = cursor.fetchall()
    conn.close()

    return render_template("admin_comment.html", comment=comment)

def delete_comment(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM comment WHERE id=?", (id,))
    conn.commit()
    conn.close()

@app.route('/delete_comment', methods=["POST"])
def delete_comment_route():
    id = request.form['id']
    delete_comment(id)
    return redirect('/admin_comment')



@app.route('/lecturer')
def lecturer():
    con = get_db_connection()
    cursor = con.cursor()

    # Fetch faculties from the database
    cursor.execute("SELECT * FROM faculty")
    faculty = cursor.fetchall()
    # Close database connection
    con.close()

    return render_template('admin_teacher_profile.html', faculties=faculty)


@app.route('/uploadlecturer', methods=["GET", "POST"])
def uploadlecturer():
    if request.method == "POST":
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        faculty = request.form.get('faculty')
        faculty_id = request.form['faculty_id']
        campus = request.form['campus']
        
        
        # Handle file upload
        photo_path = None
        if 'photo' in request.files:
            photo = request.files['photo']
            if photo.filename != '':
                # Save the file
                photo_path = os.path.join('uploads', photo.filename)
                photo.save(photo_path)

        # Set a default value if no photo is uploaded
        if photo_path is None:
            photo_path = "default_photo.jpg"  # Provide a default photo path
        
        if name and email and phone and faculty:
            con = get_db_connection()
            cursor = con.cursor()
            cursor.execute("INSERT INTO lecturer (name, email, phone, faculty, photo, campus, faculty_id) VALUES ( ?, ?, ?, ?, ?, ?,?)",
                           (name, email, phone, faculty, photo_path, campus, faculty_id))
            con.commit()
            con.close()
            return redirect('/lecturer')
        
    return redirect('/lecturer')


@app.route("/lecturerlist")
def lecturerlist():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM lecturer")
    lecturer_data = cursor.fetchall()
    conn.close()

    return render_template("lecturerlist.html", lecturers=lecturer_data)


@app.route("/edit_user/<int:id>", methods=["GET"])
def edit_user(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM lecturer WHERE id = ?", (id,))
    lecturer = cursor.fetchone()
    conn.close()
    
    if lecturer:
        return render_template("editlecturer.html", lecturer=lecturer)


    
@app.route("/update_user/<int:id>", methods=["POST"])
def update_user(id):
    name = request.form['name']
    email = request.form['email']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE lecturer SET name = ?, email = ? WHERE id = ?", (name, email, id))
    conn.commit()
    conn.close()

    return redirect("/lecturerlist")



   


if __name__ == '__main__':
    app.run(debug=True)