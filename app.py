import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, Users, Lecturer, Faculty, LecturerTemp, Comment
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Message ,Mail
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import URLSafeTimedSerializer

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)

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
    if request.method == 'POST':
        nickname = request.form['nickname']
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

        # Password validation
        if not (len(password) >= 8 and sum(c.isdigit() for c in password) >= 4) or password != confirm_password:
            error['password'] = "Password does not match or does not meet requirements"

        if not error:
            new_user = Users(nickname=nickname, email=email)
            new_user.set_password(password)  # Set hashed password
            db.session.add(new_user)
            db.session.commit()

            return redirect('/login')

        return render_template('signin.html', error=error)

    return render_template('signin.html')


@app.route('/process_login', methods=['POST'])
def process_login():
    if request.method == 'POST':
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
            flash('Invalid email or password', 'danger')
    return render_template('login.html')

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
        lecturers = faculty.lecturers
        return render_template('faculty_page.html', faculty=faculty, lecturers=lecturers)
    else:
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
    faculty_id = request.form['faculty']

    if not os.path.exists('uploads'):
        os.makedirs('uploads')

    photo.save(os.path.join('uploads/' + photo.filename))

    lecturer_temp = LecturerTemp(name=name, photo=photo.filename, phone=phone, email=email, campus=campus, faculty_id=faculty_id)
    db.session.add(lecturer_temp)
    db.session.commit()

    return redirect(url_for('keyinsuccess'))

@app.route('/lecturer/<int:lecturer_id>')
@login_required
def lecturer_details(lecturer_id):
    lecturer = Lecturer.query.get(lecturer_id)
    if not lecturer:
        return render_template('error.html', message="Lecturer not found")

    comments = Comment.query.filter_by(lecturer=lecturer.name).all()
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
        lecturer=lecturer.name,
        faculty_id=lecturer.faculty_id,
        nickname=current_user.nickname,
        comment_text=comment_text
    )

    db.session.add(new_comment)
    db.session.commit()

    return redirect(url_for('lecturer_details', lecturer_id=lecturer_id))

@app.route('/keyinsuccess')
@login_required
def keyinsuccess():
    return render_template('keyinsuccess.html')

@app.route("/index")
@login_required
def index():
    return render_template("index.html")

@app.route("/user")
@login_required
def user():
    return render_template("user.html")

@app.route("/comment")
@login_required
def comment():
    return render_template("comment.html")


@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('home'))





@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form['email']
        
        token = generate_reset_token(email)
        
        
        send_reset_email(email, token)
        

        success_message = 'Password reset email had sent successfully. Kindly check your email inbox.'
        return render_template('forgot.html', success=success_message)
    
    return render_template('forgot.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password_with_token(token):
    email = confirm_reset_token(token)
    if email:
        if request.method == 'POST':
       
            return redirect(url_for('login'))
        return render_template('reset_password_form.html')
    else:
        
        return render_template('invalid.html')



def generate_reset_token(email):
    return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])

def confirm_reset_token(token, expiration=120):
    try:
        email = serializer.loads(token, salt=app.config['SECURITY_PASSWORD_SALT'], max_age=expiration)
        return email
    except:
        return None

def send_reset_email(email, token):
    reset_link = url_for('reset_password_with_token', token=token, _external=True)
    msg = Message(
        'Password Reset',
        recipients=[email],
        body=f'We have received a request to reset your password.\n\n'
             f'To reset your password, click on the following link: {reset_link}\n\n'
             '---Eb_Comment Team---',
        sender=app.config['MAIL_DEFAULT_SENDER']
    )
    mail.send(msg)


@app.route('/reset_form', methods=['POST'])
def reset_form():
    if request.method == 'POST':
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        error= {} 


        if not (len(password) >= 8 and sum(c.isdigit() for c in password) >= 4) or password != confirm_password:
            error['password'] = "Password does not match or does not meet requirements"
            return render_template('reset_password_form.html',error=error )
        else:
            
            success_message = "Password has been updated"
            return render_template('reset_password_form.html', success=success_message)

   
    return render_template('reset_password_form.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
