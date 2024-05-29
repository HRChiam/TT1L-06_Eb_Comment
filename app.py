import os
from flask import Flask, render_template, request, redirect, url_for,flash,session
from flask_sqlalchemy import SQLAlchemy
from models import db, Users, Lecturer, Faculty, LecturerTemp
import sqlite3
from flask_login import LoginManager, login_required,logout_user,login_user
from flask_mail import Mail,Message
import logging
from itsdangerous import URLSafeTimedSerializer



app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'

def get_db_connection():
    con = sqlite3.connect('database.db')
    con.row_factory = sqlite3.Row
    return con

db.init_app(app)
mail = Mail(app)
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
logger = logging.getLogger(__name__)


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)


@app.errorhandler(404)
def page_not_found(error):
    # Render the error.html template with a custom message
    return render_template('error.html', message="Page not found"), 404

@app.errorhandler(500)
def internal_server_error(error):
    # Render the error.html template with a custom message
    return render_template('error.html', message="Internal server error"), 500


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login')
def login():       
    return render_template('login.html')


@app.route('/signin') 
def signin():
    return render_template('signin.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/process_signin', methods=['POST'])
def process_signin():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

    error = {}

    # Email validation
    if email.endswith('@student.mmu.edu.my') and len(email.split('@')[0]) == 10:
        pass
    elif email.endswith('@mmu.edu.my'):
        pass
    else:
        error['email'] = "Email invalid or does not meet requirements"

        if not (len(password) >= 8 and sum(c.isdigit() for c in password) >= 4) or password != confirm_password:
            error['password'] = "Password does not match or does not meet requirements"

        if not error:
            new_user = Users(name=username, email=email, password=password)
            db.session.add(new_user)
            db.session.commit()

            if email.endswith('@student.mmu.edu.my'):
                return redirect('/front')
            elif email.endswith('@mmu.edu.my'):
                return redirect('/index')

    return render_template('signin.html', error=error)


def send_otp_email(email, otp):
    msg = Message(
        'OTP for EbComment Account Verification',
        recipients=[email],
        body=f'Welcome to EbComment , verify your account with the OTP given.\n\n'
             f'Your OTP:{otp} \n\n'
             '---Eb_Comment Team---',
        sender=app.config['MAIL_DEFAULT_SENDER']
    )
    mail.send(msg)



@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    error = {} 
    if request.method == 'POST':
        input_otp = request.form['otp']
        if 'otp' in session and str(session['otp']) == input_otp:
            email = session.pop('email', None)
            session.pop('otp', None)
            return redirect(url_for('login'))  
        else:
            error['otp'] = "Invalid OTP, please try again"
            return render_template('otp.html', error=error)

    return render_template('otp.html')


@app.route('/process_login', methods=['POST'])
def process_login():
    email = request.form['email']
    password = request.form['password']

    user = Users.query.filter_by(email=email).first()
    
    if user and user.check_password(password):
        login_user(user)
        if email.endswith('@student.mmu.edu.my'):
            return redirect('/front')
        elif email.endswith('@mmu.edu.my'):
            return redirect('/index')

        else:
            error_message = "Email invalid or does not meet requirements"
            return render_template('login.html', error=error_message)


    return render_template('login.html')


@app.route('/forgot')
def forgot():
    return render_template('forgot.html')


@app.route('/reset_password_form')
def reset_password_form():
    return render_template('reset_password_form.html')


@app.route('/invalid')
def invalid():
    return render_template('invalid.html')


@app.route('/otp')
def otp():
    return render_template ('otp.html')


@app.route('/reset_password', methods=['POST'])
def reset_password():
    email = request.form['email']
    user = Users.query.filter_by(email=email).first()
    if user:
        token = serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])
        reset_link = url_for('reset_password_with_token', token=token, _external=True)
        send_reset_email(email, reset_link)
        flash('Password reset email has been sent.', 'info')
    else:
        flash('Email address not found.', 'danger')
    return redirect(url_for('forgot'))


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password_with_token(token):
    try:
        email = serializer.loads(token, salt=app.config['SECURITY_PASSWORD_SALT'], max_age=3600)
    except:
        flash('The reset link is invalid or has expired.', 'danger')
        return redirect(url_for('forgot'))

    if request.method == 'POST':
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('reset_password_with_token', token=token))
        user = Users.query.filter_by(email=email).first()
        if user:
            user.set_password(password)
            db.session.commit()
            flash('Your password has been updated!', 'success')
            return redirect(url_for('login'))
        else:
            flash('User not found.', 'danger')
            return redirect(url_for('forgot'))
    return render_template('reset_password_form.html', token=token)

def send_reset_email(email, reset_link):
    msg = Message('Password Reset',
                  recipients=[email],
                  body=f'We have received a request to reset your password.\n\n'
                       f'To reset your password, click on the following link: {reset_link}\n\n'
                       '---Eb_Comment Team---',)
    mail.send(msg)


@app.route('/reset_form', methods=['POST'])
def reset_form():
    password = request.form['password']
    confirm_password = request.form['confirm_password']

    error= {} 

    if not (len(password) >= 8 and sum(c.isdigit() for c in password) >= 4) or password != confirm_password:
        error['password'] = "Password does not match or does not meet requirements"
        return render_template('reset_password_form.html',error=error )
    else:
        success_message = "Password has been updated"
        return render_template('reset_password_form.html', success=success_message)


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if request.method == 'POST':
        nickname = request.form.get('nickname')
        
        success_message = 'Profile updated successfully'
        return render_template('profile.html', success=success_message)
    
    return render_template('profile.html')


@app.route('/front')
@login_required
def studentfront():
    return render_template('studentfront.html')


@app.route('/main')
@login_required
def studentmain():
    return render_template('studentmain.html')

@app.route('/faculty/<faculty_name>')
def faculty_page(faculty_name):
    # Query the database to retrieve the faculty information
    faculty = Faculty.query.filter_by(name=faculty_name).first()

    if faculty:
        # If the faculty is found, fetch information about the lecturers associated with that faculty
        lecturers = faculty.lecturers
        # Render the faculty page template with the fetched data
        return render_template('faculty_page.html', faculty=faculty, lecturers=lecturers)
    else:
        # If the faculty is not found, render an error page
        return render_template('error.html', message="Faculty not found")
    
@app.route('/keyin')
@login_required
def keyin():
    return render_template('keyin.html')


@app.route('/upload', methods=['POST'])
@login_required
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
@login_required
def keyinsuccess():
    return render_template('keyinsuccess.html')

@app.route("/index")
def index():
    return render_template("index.html")


@app.route("/user")
def user():
    return render_template("user.html")

@app.route("/comment")
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
    with app.app_context():
        db.create_all() 
    app.run(debug=True)




