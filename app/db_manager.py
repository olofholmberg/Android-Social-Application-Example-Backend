from app import models, db
from flask_jwt_extended import decode_token
from datetime import datetime

# - - - USER FUNCTIONS - - -

def register_user(username, email, password):
    user = models.User(username, email, password)
    db.session.add(user)
    db.session.commit()

def get_user_by_username(username):
    return db.session.query(models.User).filter_by(username=username).first()

def get_user_by_email(email):
    return db.session.query(models.User).filter_by(email=email).first()

def get_all_users(user):
    return db.session.query(models.User).filter(models.User.username != user.username).all()

# - - - FOLLOW FUNCTIONS - - -

def get_all_followed_users(following_user):
    return following_user.followed.all()

def add_follow_relationship(following_user, followed_user):
    following_user.follow(followed_user)
    db.session.commit()

def remove_follow_relationship(following_user, unfollowed_user):
    following_user.unfollow(unfollowed_user)
    db.session.commit()

# - - - QUESTION FUNCTIONS - - -

def add_question(question_title, question_body, user, course_room):
    question = models.Question(question_title, question_body, user, course_room)
    db.session.add(question)
    db.session.commit()

def like_question(user, question):
    user.like_question(question)
    db.session.commit()

def unlike_question(user, question):
    user.unlike_question(question)
    db.session.commit()

def get_question_by_id(id):
    return db.session.query(models.Question).filter_by(id=id).first()

# Fetches all the questions asked by users followed by user.
def get_followed_questions(user):
    return db.session.query(models.Question).join(models.followers,
                (models.followers.c.followed_id == models.Question.user_id)).filter(
                    models.followers.c.follower_id == user.id).order_by(models.Question.timestamp.desc()).all()

def get_questions_by_user(user):
    return db.session.query(models.Question).filter(models.Question.user_id == user.id).order_by(models.Question.timestamp.desc()).all()

# - - - ANSWER FUNCTIONS - - -

def add_answer(answer_body, user, parent_question):
    answer = models.Answer(answer_body, user, parent_question)
    db.session.add(answer)
    db.session.commit()

# Fetches all the answers for a question.
def get_question_answers(question):
    return db.session.query(models.Answer).filter(models.Answer.question_id == question.id).all()

# - - - COURSE FUNCTIONS - - -

def get_all_courses():
    return db.session.query(models.Course).all()

def get_course_by_code(course_code):
    return db.session.query(models.Course).filter_by(course_code=course_code).first()

# - - - TOKEN FUNCTIONS - - -

# Converts epoch timestamp to python datetime object
def _epoch_utc_to_datetime(epoch_utc):
    return datetime.fromtimestamp(epoch_utc)

def add_token_to_blacklist(encoded_token, identity_claim):
    decoded_token = decode_token(encoded_token)
    jti = decoded_token['jti']
    token_type = decoded_token['type']
    user_identity = decoded_token[identity_claim]
    expires = _epoch_utc_to_datetime(decoded_token['exp'])
    token = models.Token(jti, token_type, user_identity, expires)
    db.session.add(token)
    db.session.commit()

def is_token_revoked(decoded_token):
    jti = decoded_token['jti']
    token = db.session.query(models.Token).filter_by(jti=jti).first()
    if token is not None:
        return True
    return False

# - - - DATABASE FUNCTIONS - - -

def init_db():
    db.session.commit()
    db.drop_all()
    db.create_all()
    db.session.add(models.Course("TDDD80", "Mobile and Social Applications"))
    db.session.add(models.Course("TDDC73", "Interaction Programming"))
    db.session.add(models.Course("TATA24", "Linear Algebra"))
    db.session.commit()
