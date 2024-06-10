import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from models import db, Users, Lecturer, Faculty, LecturerTemp

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'

db.init_app(app)

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

    error = {}

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

    return render_template('signin.html')


@app.route('/process_login', methods=['GET', 'POST'])
def process_login():
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
            current_user.nickname = nickname
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

                # Process and save the new profile picture
                try:
                    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                    img_size = (140, 140)
                    img = Image.open(profile_picture)
                    img.thumbnail(img_size)
                    img.save(file_path)
                    current_user.profile_picture = filename
                    db.session.commit()
                    flash("Profile Picture Successfully Updated!", category='success')
                except Exception as e:
                    flash(f"Error updating profile picture: {e}", category='error')

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
        # If the faculty is found, fetch information about the lecturers associated with that faculty
        lecturers = faculty.lecturers
        # Render the faculty page template with the fetched data
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
    faculty_id = request.form['faculty']  # Include the faculty ID
    
    photo_filename = secure_filename(photo.filename)
    photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))

    lecturer_temp = LecturerTemp(name=name, photo=photo.filename, phone=phone, email=email, campus=campus, faculty_id=faculty_id)
    db.session.add(lecturer_temp)
    db.session.commit()

    return redirect(url_for('keyinsuccess'))


@app.route('/keyinsuccess')
@login_required
def keyinsuccess():
    return render_template('keyinsuccess.html')


@app.route("/index")
@login_required
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
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO lecturer (name, email, phone, faculty, photo, campus, faculty_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
               (name, email, phone, faculty, photo_path, campus, faculty_id))

            conn.commit()
            conn.close()
            return redirect('/lecturer')
        
    return redirect('/lecturer')

@app.route("/lecturerlist", methods=["POST", "GET"])
def lecturerlist():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM lecturer")
    lecturer_data = cursor.fetchall()
    conn.close()

    return render_template("lecturerlist.html", lecturers=lecturer_data)

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
        cursor.execute("UPDATE lecturer SET name=?, email=?, phone=?, faculty=?, campus=? WHERE id=?",
               (name, email, phone, faculty, campus, id))

        conn.commit()
        conn.close()
        return redirect('/lecturerlist')
    
    return redirect(url_for('lecturerlist'))

@app.route("/history", methods=["GET"])
def history():
    nickname = session.get("email")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM comment WHERE nickname = ?", (nickname,))
    comments = cursor.fetchall()
    conn.close()

    return render_template("admin_teacher_history.html", comments=comments)

@app.route('/admin_edit_lecturer', methods=['GET', 'POST'])
def admin_edit_lecturer():
    user_id = session.get('id')  # Using get() to avoid KeyError if 'nickname' is not in session

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    users = cursor.fetchone()
    conn.close()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM faculty")
    faculty = cursor.fetchall()
    conn.close()
    
    return render_template("admin_edit_lecturer.html", users = users,  faculties=faculty)
    

@app.route("/a_edit", methods=["POST", "GET"])
def edit_teacher():
    user_id = session.get('id')
    user_email = session.get('email')
    if request.method == "POST":
        email = request.form['email']
        campus = request.form['campus']
        bio = request.form['bio']
        phone = request.form['phone']
        faculty =request.form['faculty']



        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE lecturer SET email=?, campus=?, bio=?, phone=?, faculty=?WHERE email=?",
               ( email, campus, bio, phone,faculty, user_email))

        conn.commit()
        conn.close()

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET email=?, campus=?, bio=?, phone=?, faculty=?WHERE id=?",
               ( email, campus, bio, phone,faculty, user_id))

        conn.commit()
        conn.close()


        

    return redirect("/admin_edit_lecturer")





if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    logging.basicConfig(level=logging.INFO)
    app.run(debug=True)
