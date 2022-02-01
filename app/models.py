from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import db

# Association table for followers which represents the followed relation
# between one user and the other user.
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

# Association table for question likes which represents the liked_questions
# relation between one user and one question.
question_likes = db.Table('question_likes',
    db.Column('liker_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('liked_id', db.Integer, db.ForeignKey('question.id'))
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, index=True, unique=True)
    email = db.Column(db.String, index=True, unique=True)
    password_hash = db.Column(db.String)
    questions = db.relationship('Question', backref='author', lazy='dynamic')
    answers = db.relationship('Answer', backref='author', lazy='dynamic')

    # Relation between user and followed users
    followed = db.relationship(
        'User', # Right side entity, left side is automatically User 
        secondary=followers, # Association table
        primaryjoin=(followers.c.follower_id == id), # Left side entity link to association table
        secondaryjoin=(followers.c.followed_id == id), # Right side entity link to association table
        backref=db.backref('followers', lazy='dynamic'), # How to access using right side entity
        lazy='dynamic' # Left side query execution mode
    )

    # Relation between user and liked questions
    liked_questions = db.relationship(
        'Question',
        secondary=question_likes,
        primaryjoin=(question_likes.c.liker_id == id),
        backref=db.backref('question_likes', lazy='dynamic'),
        lazy='dynamic'
    )

    # Methods for handling following relations

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
    
    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
    
    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0
    
    # Methods for handling question likes

    def like_question(self, question):
        if not self.is_liking_question(question):
            self.liked_questions.append(question)
    
    def unlike_question(self, question):
        if self.is_liking_question(question):
            self.liked_questions.remove(question)
    
    def is_liking_question(self, question):
        return self.liked_questions.filter(question_likes.c.liked_id == question.id).count() > 0
    
    # User helper methods

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password_hash = generate_password_hash(password, salt_length=8)

    def __repr__(self):
        return '<User {}>'.format(self.username)
    
    def to_dict(self):
        return {
                "user_id": self.id,
                "username": self.username,
                "email": self.email
            }

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String, nullable=False)
    token_type = db.Column(db.String, nullable=False)
    user_identity = db.Column(db.String, nullable=False)
    expires = db.Column(db.DateTime, nullable=False)

    def __init__(self, jti, token_type, user_identity, expires):
        self.jti = jti
        self.token_type = token_type
        self.user_identity = user_identity
        self.expires = expires

    def __repr__(self):
        return '<Token {}>'.format(self.jti)

    def to_dict(self):
        return {
                "token_id": self.id,
                "jti": self.jti,
                "token_type": self.token_type,
                "user_identity": self.user_identity,
                "expires": self.expires
            }

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.String, index=True, unique=True)
    course_name = db.Column(db.String, nullable=False)
    questions = db.relationship('Question', backref='course_room', lazy='dynamic')

    def __init__(self, course_code, course_name):
        self.course_code = course_code
        self.course_name = course_name
    
    def __repr__(self):
        return '<Course {}>'.format(self.course_code)
    
    def to_dict(self):
        return {
                "course_id": self.id,
                "course_code": self.course_code,
                "course_name": self.course_name
            }

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_title = db.Column(db.String)
    question_body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    answers = db.relationship('Answer', backref='parent_question', lazy='dynamic')

    # Relationship between question and users that likes it
    likers = db.relationship(
        'User',
        secondary=question_likes,
        primaryjoin=(question_likes.c.liked_id == id),
        backref=db.backref('question_likes', lazy='dynamic'),
        lazy='dynamic'
    )

    def likes(self):
        return self.likers.count()

    def nr_answers(self):
        return db.session.query(Answer).filter(Answer.question_id == self.id).count()

    def __init__(self, question_title, question_body, author, course_room):
        self.question_title = question_title
        self.question_body = question_body
        self.author = author
        self.course_room = course_room

    def __repr__(self):
        return '<Question {}>'.format(self.question_title)
    
    def to_dict(self):
        return {
                "question_id": self.id,
                "question_title": self.question_title,
                "question_body": self.question_body,
                "timestamp": self.timestamp,
                "author": self.author.to_dict(),
                "course": self.course_room.to_dict(),
                "likes": self.likes(),
                "answers": self.nr_answers()
            }

class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    answer_body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))

    def __init__(self, answer_body, author, parent_question):
        self.answer_body = answer_body
        self.author = author
        self.parent_question = parent_question

    def __repr__(self):
        return '<Answer {}>'.format(self.answer_body)
    
    def to_dict(self):
        return {
                "answer_id": self.id,
                "answer_body": self.answer_body,
                "timestamp": self.timestamp,
                "author": self.author.to_dict()
            }
