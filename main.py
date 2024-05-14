import os
from flask import Flask, render_template, request, redirect, url_for
from wtforms import StringField, SubmitField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from models import db, Users, Lecturer

# Create Flask app
app = Flask(__name__)

# Configure SQLite DB URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'

# Initialize SQLAlchemy
db.init_app(app)

# Routes
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
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        error= {}

        # Check email format
        if email.endswith('@student.mmu.edu.my') and len(email.split('@')[0]) == 10:
            pass
        elif email.endswith('@mmu.edu.my'):
            pass
        else:
            error['email'] = "Email invalid or does not meet requirements"

        # Check password format and match
        if not (len(password) >= 8 and sum(c.isdigit() for c in password) >= 4) or password != confirm_password:
            error['password'] = "Password does not match or does not meet requirements"

        # If no errors, save user information
        if not error:
            # Create a new Users object and add it to the session
            new_user = Users(name=username, email=email, password=password, phone_number='')  # Add phone_number if needed
            db.session.add(new_user)
            db.session.commit()

            # Redirect to the appropriate page
            if email.endswith('@student.mmu.edu.my'):
                return redirect('/front')
            elif email.endswith('@mmu.edu.my'):
                return redirect('/index')

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

@app.route("/index")
def index():
    return render_template("index.html")

@app.route("/user")
def user():
    return render_template("user.html")

@app.route("/comment")
def comment():
    return render_template("comment.html")

if __name__ == '__main__':
    with app.app_context():
        db.create_all() 
    app.run(debug=True)