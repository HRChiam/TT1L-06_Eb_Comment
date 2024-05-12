import os
from flask import Flask, render_template, request, redirect, url_for
from models import db, User

web = Flask(__name__)
web.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/User/Projects/Student/database.db'
db.init_app(web)

@web.route('/')
def studentfront():
    return render_template('studentfront.html')

@web.route('/main')
def studentmain():
    return render_template('studentmain.html')

Lecturers = []

@web.route('/keyin')
def keyin():
    return render_template('keyin.html')

@web.route('/upload', methods = ['POST'])
def upload():
    name = request.form['name']
    photo = request.files['photo']
    phone = request.form['phone']
    email = request.form['email']

    if not os.path.exists('uploads'):
        os.makedirs('uploads')

    photo.save(os.path.join('uploads/' + photo.filename))

    lecturer_info = {
        'name': name,
        'photo': photo.filename,
        'phone': phone,
        'email': email
    }

    Lecturers.append(lecturer_info)

    return redirect(url_for('keyinsuccess'))

@web.route('/keyinsuccess')
def keyinsuccess():
    return render_template('keyinsuccess.html')

if __name__ == '__main__':
    with web.app_context():
        db.create_all() 
    web.run(debug=True)