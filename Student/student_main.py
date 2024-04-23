from flask import Flask, render_template, request, redirect, url_for

web = Flask(__name__)

Lecturers = []

@web.route('/')
def keyin():
    return render_template('keyin.html')

@web.route('/upload', methods = ['POST'])
def upload():
    name = request.form['name']
    photo = request.files['photo']
    phone = request.form['phone']
    email = request.form['email']

    photo.save('uploads/' + photo.filename)

    lecturer_info = {
        'name': name,
        'photo': photo.filename,
        'phone': phone,
        'email': email
    }

    Lecturers.append(lecturer_info)

    return redirect(url_for('success'))

@web.route('/keyinsuccess')
def keyinsuccess():
    return render_template('keyinsuccess.html')

if __name__ == '__main__':
    web.run(debug = True)