from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import date


db = SQLAlchemy()

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    profile_picture = db.Column(db.String(256), nullable=False, default = 'default_profile_photo.jpg')
    role = db.Column(db.String(50), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<Name %r>' % self.name


class Faculty(db.Model):
    __tablename__ = 'faculty'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique = True)
    campus = db.Column(db.String(100), nullable=False)
    lecturers = db.relationship("Lecturer", back_populates="faculty", lazy = True)
    lecturers_temp = db.relationship("LecturerTemp", back_populates="faculty", lazy = True)

class LecturerTemp(db.Model):
    __tablename__ = 'lecturer_temp'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    photo = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    campus = db.Column(db.String(100), nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id'), nullable=False)
    faculty = db.relationship("Faculty", back_populates="lecturers_temp")
    status = db.Column(db.String(20), nullable=False, default='pending')

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
    faculty = db.relationship("Faculty", back_populates="lecturers")

class Comment(db.Model):
    __tablename__ = 'comment'

    id = db.Column(db.Integer, primary_key=True)
    lecturer_id = db.Column(db.Integer, ForeignKey('lecturer.id'), nullable=False)
    faculty_id = db.Column(db.Integer, ForeignKey('faculty.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    comment_text = db.Column(db.Text, nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    time = db.Column(db.Time, nullable=False, default=datetime.now().time)
    reactions = db.relationship('CommentReaction', backref='comment', lazy='dynamic')

    def likes_count(self):
        return CommentReaction.query.filter_by(comment_id=self.id, reaction=True).count()

    def dislikes_count(self):
        return CommentReaction.query.filter_by(comment_id=self.id, reaction=False).count()
    
    def has_reaction(self, user, reaction):
        return CommentReaction.query.filter_by(comment_id=self.id, user_id=user.id, reaction=reaction).first() is not None

class CommentReaction(db.Model):
    __tablename__ = 'comment_reactions'

    id = db.Column(db.Integer, primary_key=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reaction = db.Column(db.Boolean, nullable=False)  #True for like, False for dislike

    def __init__(self, comment_id, user_id, reaction):
        self.comment_id = comment_id
        self.user_id = user_id
        self.reaction = reaction
