from flask import Flask, render_template, url_for

# app = Flask(__name__)
app = Flask(__name__, static_folder='static')


@app.route('/')
def home():
    return render_template ('home.html')

@app.route('/login')
def login():
    return render_template ('login.html')

@app.route('/signin')
def signin():
    return render_template ('signin.html')


if __name__=='__main__':
   app.run(debug=True)

    
# from flask import Flask, render_template, request, redirect, url_for

# web = Flask(__name__)

# Lecturers = []

# @web.route('/')
# def keyin():
#     return render_template('keyin.html')

# @web.route('/upload', methods = ['POST'])
# def upload():
#     name = request.form['name']
#     photo = request.files['photo']
#     phone = request.form['phone']
#     email = request.form['email']

#     photo.save('uploads/' + photo.filename)

#     lecturer_info = {
#         'name': name,
#         'photo': photo.filename,
#         'phone': phone,
#         'email': email
#     }

#     Lecturers.append(lecturer_info)

#     return redirect(url_for('keyinsuccess'))

# @web.route('/keyinsuccess')
# def keyinsuccess():
#     return render_template('keyinsuccess.html')

# if __name__ == '__main__':
#     web.run(debug = True)











