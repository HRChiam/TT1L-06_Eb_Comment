from datetime import datetime
from flask import Flask, request, render_template , request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Message ,Mail
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import URLSafeTimedSerializer


app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['MAIL_SERVER'] = 'smtp-mail.outlook.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL']= False 
app.config['MAIL_USERNAME'] = 'ebcomment123@outlook.my'
app.config['MAIL_PASSWORD'] = 'hjszkqeytfsdnldp'
app.config['MAIL_DEFAULT_SENDER'] ='ebcomment123@outlook.my'

app.secret_key = 'your_secret_key_here'
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SECURITY_PASSWORD_SALT'] = 'your_salt'

db = SQLAlchemy(app)
mail = Mail(app)
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

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


@app.route('/reset_password_form')
def reset_password_form():
    return render_template ('reset_password_form.html')


@app.route('/invalid')
def invalid():
    return render_template('invalid.html')




@app.route('/process_login', methods=['GET', 'POST'])
def process_login():
    if request.method == 'POST':
        # username = request.form['username']
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




@app.route('/process_signin', methods=['POST'])
def process_signin():
    if request.method == 'POST':
        email = request.form['email']
        nickname = request.form['nickname']
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
    app.run(debug=True)