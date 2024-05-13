from typing import Dict
from flask import Flask, request, render_template , request, redirect, url_for


app = Flask(__name__, template_folder='templates')


@app.route('/')
def home():
    return render_template ('home.html')


@app.route('/signin')
def signin():
    return render_template('signin.html')


@app.route('/login')
def login():
    return render_template ('login.html')


@app.route('/forgot')
def forgot():
    return render_template ('forgot.html')


@app.route('/profile')
def profile():
    return render_template ('profile.html')


@app.route('/student')
def student():
    return render_template('student.html')


@app.route('/lec')
def lec():
    return render_template('lec.html')




@app.route('/process_login', methods=['GET', 'POST'])
def process_login():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

     
        student_email = email.endswith('@student.mmu.edu.my')and len(email.split('@')[0]) == 10

        if student_email:
            return redirect(url_for('student')) 
        

        elif email.endswith('@mmu.edu.my'):
            return redirect(url_for('lec'))

        else:
            error_message = "Email invalid or does not meet requirements"
            return render_template('login.html', error=error_message)


    return render_template('login.html')




# def requirement_password(password):
    
#     if len(password) < 8:
#         return False
    
#     digit_count = sum(c.isdigit() for c in password)
#     if digit_count < 4:
#         return False
#     return True




@app.route('/process_signin', methods=['POST'])
def process_signin():
    if request.method == 'POST':
        username = request.form['username']
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

        
        if not error and email.endswith('@student.mmu.edu.my'):
            return redirect(url_for('student'))
        

        if not error and email.endswith('@mmu.edu.my'):
            return redirect(url_for('lec'))


        return render_template('signin.html', error=error)

    
    return render_template('signin.html')



if __name__ == '__main__':
    app.run(debug=True)










