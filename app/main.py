import os
import logging
import random
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from app.models import db, Users, Lecturer, Faculty, LecturerTemp, Comment, CommentReaction
from datetime import datetime, date
from flask_mail import Message, Mail
from itsdangerous import URLSafeTimedSerializer
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from PIL import Image
from functools import wraps

otp_storage = {}
load_dotenv()

app = Flask(__name__, instance_relative_config=True)

if not os.path.exists(app.instance_path):
    os.makedirs(app.instance_path)

def get_db_connection():
    con = sqlite3.connect("instance/database.db")
    con.row_factory = sqlite3.Row
    return con

DATABASE_NAME = "database.db"
DATABASE_PATH = os.path.join(app.instance_path, DATABASE_NAME)

app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DATABASE_PATH}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_secret_key')
app.config['MAIL_SERVER'] = 'smtp-mail.outlook.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', 'ebcomment123@outlook.my')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', 'hjszkqeytfsdnldp')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', 'ebcomment123@outlook.my')
app.config['SECURITY_PASSWORD_SALT'] = os.getenv('SECURITY_PASSWORD_SALT', 'your_security_password_salt')
app.config['UPLOAD_FOLDER'] = 'app/static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

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

def roles_required(*roles):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if current_user.role not in roles:
                abort(403)  # Forbidden
            return f(*args, **kwargs)
        return wrapped
    return wrapper

@app.errorhandler(404)
def page_not_found(error):
    return render_template('error.html', message="Page not found"), 404


@app.errorhandler(500)
def internal_server_error(error):
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
    email = request.form['email']
    nickname = request.form['nickname']
    password = request.form['password']
    confirm_password = request.form['confirm_password']

    error = {}

    # Email validation
    if email.endswith('@student.mmu.edu.my') and len(email.split('@')[0]) == 10:
        role = 'student'
    elif email.endswith('@mmu.edu.my'):
        role = 'lecturer'
    else:
        error['email'] = "Email invalid or does not meet requirements"

    # Password validation
    if not (len(password) >= 8 and sum(c.isdigit() for c in password) >= 4) or password != confirm_password:
        error['password'] = "Password does not match or does not meet requirements"

    
    if not error:
    # Create and add new user to the database
        if email.endswith('@mmu.edu.my'):
            new_user = Users(name=nickname, email=email, role = role)
            new_user.set_password(password)  # Set hashed password
            db.session.add(new_user)

            # Create a new lecturer using Lecturer class
            new_lecturer = Lecturer(
                name=nickname,
                email=email,
                photo="default_photo.jpg",  # Provide a default value for the photo attribute
                phone="123456789",  # Provide a value for the phone attribute
                campus="Cyberjaya",  # Provide a value for the campus attribute
                bio="None",     # Provide a value for the bio attribute, if applicable
                faculty_id="0",  # Provide a value for the faculty_id attribute
            )
            db.session.add(new_lecturer)

            db.session.commit()
        else:
            new_user = Users(name=nickname, email=email, role = role)
            new_user.set_password(password)  # Set hashed password
            db.session.add(new_user)

            db.session.commit()

        # # Check email domain and send OTP if applicable
        if email.endswith('@student.mmu.edu.my') or email.endswith('@mmu.edu.my'):
            otp = random.randint(100000, 999999)
            session['otp'] = otp
            session['email'] = email
            send_otp_email(email, otp)
            return redirect(url_for('otp'))
    

        return redirect('/login')

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
     # Retrieve nickname from form data

    if email == 'admin@gmail.com' and password == 'abc':
        session['email'] = 'admin@gmail.com'
        return redirect('/admin')

    user = Users.query.filter_by(email=email).first()

    if user and user.check_password(password):
        login_user(user)
        if email.endswith('@student.mmu.edu.my'):
            session['email'] = email
            session['user_id'] = user.id
            return redirect('/front')
        elif email.endswith('@mmu.edu.my'):
            session['email'] = email
            session['user_id'] = user.id
            return redirect('/admin')
    else:
        flash('Invalid email or password', 'danger')
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


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        nickname = request.form.get('nickname')

        if nickname:
            current_user.name = nickname
            db.session.commit()

        if 'profile_picture' in request.files:
            profile_picture = request.files['profile_picture']

            if profile_picture and allowed_file(profile_picture.filename):
                filename = secure_filename(profile_picture.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

                # Remove previous profile picture if it's not the default
                previous_profile_picture = current_user.profile_picture
                if previous_profile_picture != "default_pfp.png":
                    previous_file_path = os.path.join(app.config['UPLOAD_FOLDER'], previous_profile_picture)
                    if os.path.exists(previous_file_path):
                        os.remove(previous_file_path)

                    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                    img_size = (140, 140)
                    img = Image.open(profile_picture)
                    img.thumbnail(img_size)
                    img.save(file_path)
                    current_user.profile_picture = filename
                    db.session.commit()

    return render_template('profile.html', user=current_user)


@app.route('/front')
@login_required
def studentfront():
    return render_template('studentfront.html')


@app.route('/main')
@login_required
def studentmain():
    return render_template('studentmain.html')


@app.route('/faculty/<faculty_name>')
@login_required
def faculty_page(faculty_name):
    faculty = Faculty.query.filter_by(name=faculty_name).first()

    if faculty:
        lecturers = Lecturer.query.filter_by(faculty_id=faculty.id).all()  # Fetch lecturers for the specific faculty
        return render_template('faculty_page.html', faculty=faculty, lecturers=lecturers)
    else:
        return render_template('error.html', message="Faculty not found")


@app.route('/lecturer/<int:lecturer_id>')
@login_required
def lecturer_details(lecturer_id):
    # Fetch the lecturer using the lecturer_id
    lecturer = Lecturer.query.get(lecturer_id)
    
    # If the lecturer does not exist, render an error page
    if not lecturer:
        return render_template('error.html', message="Lecturer not found")

    # Filter comments based on the lecturer_id
    comments = Comment.query.filter_by(lecturer_id=lecturer_id).all()
    
    # Render the lecturer details page with the fetched lecturer and comments
    return render_template('lecturer_page.html', lecturer=lecturer, comments=comments)


@app.route('/add_comment', methods=['POST'])
@login_required
def add_comment():
    lecturer_id = request.form['lecturer_id']
    comment_text = request.form['comment_text']
    
    lecturer = Lecturer.query.get(lecturer_id)
    if not lecturer:
        return render_template('error.html', message="Lecturer not found")

    new_comment = Comment(
        lecturer_id=lecturer.id,
        faculty_id=lecturer.faculty_id,
        name=current_user.name,
        comment_text=comment_text,
        date=date.today(),
        time=datetime.now().time()
    )

    db.session.add(new_comment)
    db.session.commit()

    return redirect(url_for('lecturer_details', lecturer_id=lecturer_id))


@app.route('/upvote_comment/<int:comment_id>', methods=['POST'])
@login_required
def upvote_comment(comment_id):
    comment = Comment.query.get(comment_id)
    if comment:
        reaction = CommentReaction.query.filter_by(comment_id=comment_id, user_id=current_user.id).first()
        if reaction:
            if not reaction.reaction:  #if it's a dislike, toggle to like
                reaction.reaction = True
            else:  #if it's a like, toggle to no reaction
                db.session.delete(reaction)
        else:
            reaction = CommentReaction(comment_id=comment_id, user_id=current_user.id, reaction=True)
            db.session.add(reaction)
        db.session.commit()
    return jsonify({'likes': comment.likes_count(), 'dislikes': comment.dislikes_count()})


@app.route('/downvote_comment/<int:comment_id>', methods=['POST'])
@login_required
def downvote_comment(comment_id):
    comment = Comment.query.get(comment_id)
    if comment:
        reaction = CommentReaction.query.filter_by(comment_id=comment_id, user_id=current_user.id).first()
        if reaction:
            if reaction.reaction:  #if it's a like, toggle to dislike
                reaction.reaction = False
            else:  #if it's a dislike, toggle to no reaction
                db.session.delete(reaction)
        else:
            reaction = CommentReaction(comment_id=comment_id, user_id=current_user.id, reaction=False)
            db.session.add(reaction)
        db.session.commit()
    return jsonify({'likes': comment.likes_count(), 'dislikes': comment.dislikes_count()})


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
    faculty_id = request.form['faculty']

    if request.method == 'POST':
        name = request.form.get('name')

        if 'photo' in request.files:
            photo = request.files['photo']

            if photo and allowed_file(photo.filename):
                filename = secure_filename(photo.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)                
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                img_size = (140, 140)
                img = Image.open(photo)
                img.thumbnail(img_size)
                img.save(file_path)
                lecturer.photo = filename
                db.session.commit()

    lecturer_temp = LecturerTemp(name=name, photo=photo.filename, phone=phone, email=email, campus=campus, faculty_id=faculty_id)
    db.session.add(lecturer_temp)
    db.session.commit()

    return redirect(url_for('keyinsuccess'))


@app.route('/keyinsuccess')
@login_required
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

def delete_user(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id=?", (id,))
    conn.commit()
    conn.close()

@app.route('/delete_user', methods=["POST"])
def delete_user_route():
    id = request.form['id']
    delete_user(id)
    return redirect('/user')

def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@app.route('/admin/view_lecturers_temp')
def view_lecturers_temp():
    lecturers_temp = LecturerTemp.query.all()

    return render_template('view_lecturers_temp.html', lecturers_temp=lecturers_temp)

@app.route('/admin/approve_lecturer/<int:lecturer_id>', methods=['POST'])
def approve_lecturer(lecturer_id):
    lecturer_temp = LecturerTemp.query.get_or_404(lecturer_id)
    
    lecturer = Lecturer(
        name=lecturer_temp.name,
        photo=lecturer_temp.photo,
        phone=lecturer_temp.phone,
        email=lecturer_temp.email,
        campus=lecturer_temp.campus,
        faculty_id=lecturer_temp.faculty_id,  # Ensure faculty ID is transferred
    )

    db.session.add(lecturer)
    db.session.delete(lecturer_temp)
    db.session.commit()

    return redirect(url_for('view_lecturers_temp'))


@app.route('/admin/reject_lecturer/<int:lecturer_id>', methods=['POST'])
def reject_lecturer(lecturer_id):
    lecturer_temp = LecturerTemp.query.get_or_404(lecturer_id)
    db.session.delete(lecturer_temp)
    db.session.commit()
    
    return redirect(url_for('view_lecturers_temp'))


@app.route("/admin_comment")
def comment():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT comment.id, lecturer.name as lecturer_name, faculty.name as faculty_name, comment.name, comment.comment_text, comment.date, comment.time 
        FROM comment 
        JOIN lecturer ON comment.lecturer_id = lecturer.id 
        JOIN faculty ON comment.faculty_id = faculty.id
    """)
    comments = cursor.fetchall()
    conn.close()
    
    return render_template("admin_comment.html", comments=comments)



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
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM faculty")
    faculty = cursor.fetchall()
    conn.close()

    return render_template('admin_teacher_profile.html', faculties=faculty)



@app.route('/uploadlecturer', methods=["GET", "POST"])
def uploadlecturer():
    if request.method == "POST":
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        faculty = request.form.get('faculty')
        faculty_id = request.form.get('faculty_id')
        campus = request.form.get('campus')
        
        # Handle file upload

        
        if name and email and phone and faculty:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO lecturer (name, email, phone, faculty, campus, faculty_id) VALUES (?, ?, ?, ?, ?, ?)",
               (name, email, phone, faculty, campus, faculty_id))

            conn.commit()
            conn.close()
            return redirect('/lecturer')
        
    return redirect('/lecturer')

@app.route("/lecturerlist", methods=["POST", "GET"])
def lecturerlist():
    lecturers = db.session.query(Lecturer).join(Faculty).add_columns(
        Lecturer.id,
        Lecturer.name,
        Lecturer.email,
        Lecturer.phone,
        Lecturer.campus,
        Faculty.name.label('faculty_name')
    ).all()

    return render_template("lecturerlist.html", lecturers=lecturers)


def delete_lecturer(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM lecturer WHERE id=?", (id,))
    conn.commit()
    conn.close()

@app.route('/delete_lecturer', methods=["POST", "GET"])
def delete_lecturer_route():
    if request.method == 'GET':
        id = request.args.get('id')  # Access data from query string using request.args
    else:
        id = request.form['id']  # Access data from form data for POST requests (optional)

    delete_lecturer(id)
    return redirect('/lecturerlist')

@app.route("/edit_user/<int:id>", methods=["GET", "POST"])
def edit_user(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM lecturer WHERE id = ?", (id,))
    lecturer = cursor.fetchone()
    conn.close()

    if request.method == "POST":
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        faculty = request.form.get('faculty')
        campus = request.form.get('campus')

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE lecturer SET name=?, email=?, phone=?, faculty=?, campus=?,  WHERE id=?",
                       (name, email, phone, faculty, campus, id))
        conn.commit()
        conn.close()
        return redirect('/lecturer')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM faculty")
    faculty = cursor.fetchall()
    conn.close()
    
    if lecturer:
        return render_template("editlecturer.html", lecturer=lecturer, faculties=faculty)

    
@app.route("/update_user/<int:id>", methods=["POST"])
def update_user(id):

    if request.method == "POST":
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        faculty = request.form.get('faculty')
        campus = request.form.get('campus')

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE lecturer SET name=?, email=?, phone=?, faculty_id=?, campus=? WHERE id=?",
               (name, email, phone, faculty, campus, id))

        conn.commit()
        conn.close()
        return redirect('/lecturerlist')
    
    return redirect(url_for('lecturerlist'))

@app.route("/history", methods=["GET"])
def history():
    email = session.get("email")  # Assuming the email is stored in the session
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Retrieve lecturer ID based on email
    cursor.execute("SELECT id FROM lecturer WHERE email = ?", (email,))
    lecturer_id = cursor.fetchone()[0]  # Assuming email is unique, fetch the first result
    
    # Fetch comments associated with the lecturer's ID and join with users and faculty tables
    cursor.execute("""
        SELECT comment.id, comment.comment_text, comment.date, comment.time, 
               comment.name, faculty.name as faculty_name 
        FROM comment 
        JOIN faculty ON comment.faculty_id = faculty.id
        WHERE comment.lecturer_id = ?
    """, (lecturer_id,))
    comments = cursor.fetchall()
    
    conn.close()

    return render_template("admin_teacher_history.html", comments=comments)


@app.route("/a_edit", methods=["POST", "GET"])
def edit_teacher():
    user_id = session.get('id')
    user_email = session.get('email')

    email = session.get('email')  # Correct key to retrieve user email from session
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Retrieve lecturer ID based on email
    cursor.execute("SELECT id FROM lecturer WHERE email = ?", (email,))
    lecturer_id = cursor.fetchone()[0]  # Assuming email is unique, fetch the first result
    
    # Retrieve lecturer information based on ID
    cursor.execute("SELECT * FROM lecturer WHERE id = ?", (lecturer_id,))
    lecturers = cursor.fetchone()
    
    # Retrieve faculties
    cursor.execute("SELECT * FROM faculty")
    faculties = cursor.fetchall()
    
    conn.close()

    if request.method == "POST":
        email = request.form['email']
        campus = request.form['campus']
        bio = request.form['bio']
        phone = request.form['phone']
        faculty_id = request.form['faculty']

        photo_filename = None
        if 'photo' in request.files:
            photo = request.files['photo']

            if photo and allowed_file(photo.filename):
                filename = secure_filename(photo.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                img_size = (140, 140)
                img = Image.open(photo)
                img.thumbnail(img_size)
                img.save(file_path)
                photo_filename = filename

        # Update lecturer details
        with get_db_connection() as conn:
            cursor = conn.cursor()
            if photo_filename:
                cursor.execute(
                    "UPDATE lecturer SET email=?, campus=?, bio=?, phone=?, faculty_id=?, photo=? WHERE email=?",
                    (email, campus, bio, phone, faculty_id, photo_filename, user_email)
                )
            else:
                cursor.execute(
                    "UPDATE lecturer SET email=?, campus=?, bio=?, phone=?, faculty_id=? WHERE email=?",
                    (email, campus, bio, phone, faculty_id, user_email)
                )
            conn.commit()

        # Update user email
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET email=? WHERE id=?", (email, user_id))
            conn.commit()

        return redirect("/admin_edit_lecturer")

    # Render the edit form or other appropriate response for GET requests
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM lecturer WHERE email=?", (user_email,))
        lecturer = cursor.fetchone()

    return render_template("admin_edit_lecturer.html", lecturers=lecturers, faculties=faculties)


# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()
#     logging.basicConfig(level=logging.INFO)
#     app.run(debug=True)
