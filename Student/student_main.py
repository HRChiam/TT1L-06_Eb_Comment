import os
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy

web = Flask(__name__)
web.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://KEEHUIYEE:KeE-0924@127.0.0.1/users'
db = SQLAlchemy(web)

class Lecturer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    photo = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(100), nullable=False)

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@web.route('/')
def studentfront():
    return render_template('studentfront.html')

@web.route('/main')
def studentmain():
    return render_template('studentmain.html')

@web.route('/keyin')
def keyin():
    return render_template('keyin.html')

@web.route('/upload', methods = ['POST'])
def upload():
    name = request.form['name']
    photo = request.files['photo']
    phone = request.form['phone']
    email = request.form['email']

    if photo and allowed_file(photo.filename):
        filename = secure_filename(photo.filename)
        photo.save(os.path.join('uploads', filename))

        lecturer = Lecturer(name=name, photo=filename, phone=phone, email=email)
        db.session.add(lecturer)
        db.session.commit()

        return redirect(url_for('keyinsuccess'))

    return "Invalid file format"

@web.route('/keyinsuccess')
def keyinsuccess():
    return render_template('keyinsuccess.html')

if __name__ == '__main__':
    db.create_all
    web.run(debug = True)
