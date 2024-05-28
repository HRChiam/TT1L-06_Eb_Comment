# from datetime import datetime
# from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy import ForeignKey
# from sqlalchemy.orm import relationship
# from werkzeug.security import generate_password_hash, check_password_hash

# db = SQLAlchemy()


# class Users(db.Model):
#     name = db.Column(db.String(20), primary_key=True)
#     email = db.Column(db.String(200), nullable=False)
#     password = db.Column(db.String(20), nullable=False)

#     def __repr__(self):
#         return '<Name %r>' % self.name
    

# class Faculty(db.Model):
#     __tablename__ = 'faculty'

#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), nullable=False)
#     campus = db.Column(db.String(100), nullable=False)
#     lecturers = relationship("Lecturer", back_populates="faculty")

# class LecturerTemp(db.Model):
#     __tablename__ = 'lecturer_temp'

#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), nullable=False)
#     photo = db.Column(db.String(100), nullable=False)
#     phone = db.Column(db.String(20), nullable=False)
#     email = db.Column(db.String(200), nullable=False)
#     campus = db.Column(db.String(100), nullable=False)
#     faculty_id = db.Column(db.Integer, ForeignKey('faculty.id'), nullable=False)
#     faculty = relationship("Faculty")
    
# class Lecturer(db.Model):
#     __tablename__ = 'lecturer'

#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), nullable=False)
#     photo = db.Column(db.String(100), nullable=False)
#     phone = db.Column(db.String(20), nullable=False)
#     email = db.Column(db.String(200), nullable=False)
#     campus = db.Column(db.String(100), nullable=False)
#     faculty_id = db.Column(db.Integer, ForeignKey('faculty.id'), nullable = False)
#     faculty = relationship("Faculty", back_populates="lecturers")

# class Comment(db.Model):
#     __tablename__ = 'comment'

#     id = db.Column(db.Integer, primary_key=True)
#     lecturer = db.Column(db.String(100), nullable=False)
#     faculty_id = db.Column(db.Integer, ForeignKey('faculty.id'), nullable=False)
#     username = db.Column(db.String(100), nullable=False)
#     comment_text = db.Column(db.Text, nullable=False)
#     date = db.Column(db.Date, nullable=False, default=datetime.now().date())
#     time = db.Column(db.Time, nullable=False, default=datetime.now().time())
#     faculty = relationship("Faculty")




from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()


from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)



class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nickname = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<Name %r>' % self.nickname


class Faculty(db.Model):
    __tablename__ = 'faculty'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    campus = db.Column(db.String(100), nullable=False)
    lecturers = relationship("Lecturer", back_populates="faculty")

class LecturerTemp(db.Model):
    __tablename__ = 'lecturer_temp'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    photo = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    campus = db.Column(db.String(100), nullable=False)
    faculty_id = db.Column(db.Integer, ForeignKey('faculty.id'), nullable=False)
    faculty = relationship("Faculty")

class Lecturer(db.Model):
    __tablename__ = 'lecturer'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    photo = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    campus = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.Text, nullable=True) 
    faculty_id = db.Column(db.Integer, ForeignKey('faculty.id'), nullable=False)
    faculty = relationship("Faculty", back_populates="lecturers")

class Comment(db.Model):
    __tablename__ = 'comment'

    id = db.Column(db.Integer, primary_key=True)
    lecturer_id = db.Column(db.Integer, ForeignKey('lecturer.id'), nullable=False)
    faculty_id = db.Column(db.Integer, ForeignKey('faculty.id'), nullable=False)
    nickname = db.Column(db.String(100), nullable=False)
    comment_text = db.Column(db.Text, nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    time = db.Column(db.Time, nullable=False, default=datetime.now().time)
    likes = db.relationship('Users', secondary='comment_likes', backref=db.backref('liked_comments', lazy='dynamic'))
    dislikes = db.relationship('Users', secondary='comment_dislikes', backref=db.backref('disliked_comments', lazy='dynamic'))

    def likes_count(self):
        return len(self.likes)

    def dislikes_count(self):
        return len(self.dislikes)

comment_likes = db.Table('comment_likes',
    db.Column('comment_id', db.Integer, db.ForeignKey('comment.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'))
)

comment_dislikes = db.Table('comment_dislikes',
    db.Column('comment_id', db.Integer, db.ForeignKey('comment.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'))
)