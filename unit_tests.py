import os
import unittest
import tempfile
from flask import json
from app import app, db_manager

class TestCase(unittest.TestCase):

    def setUp(self):
        temp_db = tempfile.mkstemp()
        basedir = os.path.abspath(os.path.dirname(temp_db[1]))
        self.db_fd = temp_db[0]
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, temp_db[1])
        app.testing = True
        self.app = app.test_client()
        with app.app_context():
            db_manager.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        # Omitt the 'sqlite:///' part with [10:] when removing temp_db on
        # windows, will cause [WinError 123] otherwise.
        os.unlink(app.config['SQLALCHEMY_DATABASE_URI'][10:])
    
    # - - - INDEX TEST - - -

    def test_index(self):
        rv = self.app.get('/')
        assert rv.data == b"Hi there!"
    
    # - - - REGISTRATION TESTS - - -

    def test_registration(self):
        # Users
        u1 = {"username": "nammers1","email": "namn.namnsson@test.com","password": "namn123"}
        # Register users
        rv_add_u1 = self.app.post('/users', data=json.dumps(u1), content_type='application/json')
        # Assert that the registration was successful
        assert rv_add_u1.json["msg"] == "User successfully registered"
    
    def test_registration_duplicate_email(self):
        # Users
        u1 = {"username": "nammers1","email": "namn.namnsson@test.com","password": "namn123"}
        u2 = {"username": "nammers2","email": "namn.namnsson@test.com","password": "namn456"}
        # Register users
        rv_add_u1 = self.app.post('/users', data=json.dumps(u1), content_type='application/json')
        rv_add_u2 = self.app.post('/users', data=json.dumps(u2), content_type='application/json')
        # Assert that the second registration failed
        assert rv_add_u2.json["msg"] == "Email is already registered"
    
    def test_registration_duplicate_username(self):
        # Users
        u1 = {"username": "nammers1","email": "namn.namnsson@test.com","password": "namn123"}
        u2 = {"username": "nammers1","email": "namn.efernamn@test.com","password": "namn456"}
        # Register users
        rv_add_u1 = self.app.post('/users', data=json.dumps(u1), content_type='application/json')
        rv_add_u2 = self.app.post('/users', data=json.dumps(u2), content_type='application/json')
        # Assert that the second registration failed
        assert rv_add_u2.json["msg"] == "Username is already taken"
    
    # - - - LOGIN TESTS - - -

    def test_login(self):
        # Users
        u1 = {"username": "nammers1","email": "namn.namnsson@test.com","password": "namn123"}
        # Register users
        rv_add_u1 = self.app.post('/users', data=json.dumps(u1), content_type='application/json')
        # Login user 1
        rv_login_u1 = self.app.post('/login', data=json.dumps({"email": u1["email"], "password": u1["password"]}), content_type='application/json')
        # Assert that the login succeeded
        assert rv_login_u1.json["token_type"] == "Bearer"
    
    def test_login_wrong_email(self):
        # Users
        u1 = {"username": "nammers1","email": "namn.namnsson@test.com","password": "namn123"}
        # Register users
        rv_add_u1 = self.app.post('/users', data=json.dumps(u1), content_type='application/json')
        # Login user 1
        rv_login_u1 = self.app.post('/login', data=json.dumps({"email": "namn.efternamn@test.com", "password": u1["password"]}), content_type='application/json')
        # Assert that the login failed
        assert rv_login_u1.json["msg"] == "Wrong email"

    def test_login_wrong_password(self):
        # Users
        u1 = {"username": "nammers1","email": "namn.namnsson@test.com","password": "namn123"}
        # Register users
        rv_add_u1 = self.app.post('/users', data=json.dumps(u1), content_type='application/json')
        # Login user 1
        rv_login_u1 = self.app.post('/login', data=json.dumps({"email": u1["email"], "password": "wrongpass"}), content_type='application/json')
        # Assert that the login failed
        assert rv_login_u1.json["msg"] == "Wrong password"
    
    def test_refresh_token(self):
        # Users
        u1 = {"username": "nammers1","email": "namn.namnsson@test.com","password": "namn123"}
        # Register users
        rv_add_u1 = self.app.post('/users', data=json.dumps(u1), content_type='application/json')
        # Login user 1
        rv_login_u1 = self.app.post('/login', data=json.dumps({"email": u1["email"], "password": u1["password"]}), content_type='application/json')
        acc_token_u1_1 = rv_login_u1.json["token_type"] + " " + rv_login_u1.json["access_token"]
        # Get a new access token for user 1
        rv_refresh_token_u1 = self.app.post('/refresh_token', headers={"Authorization": acc_token_u1_1})
        # Assert that a new token was received
        assert rv_refresh_token_u1.json["token_type"] == "Bearer"
    
    def test_logout(self):
        # Users
        u1 = {"username": "nammers1","email": "namn.namnsson@test.com","password": "namn123"}
        # Register users
        rv_add_u1 = self.app.post('/users', data=json.dumps(u1), content_type='application/json')
        # Login user 1
        rv_login_u1 = self.app.post('/login', data=json.dumps({"email": u1["email"], "password": u1["password"]}), content_type='application/json')
        acc_token_u1_1 = rv_login_u1.json["token_type"] + " " + rv_login_u1.json["access_token"]
        # Logout user 1
        rv_refresh_token_u1 = self.app.post('/logout', headers={"Authorization": acc_token_u1_1})
        # Assert correct token was revoked
        assert rv_refresh_token_u1.json["msg"] == "Logout successful"

    # - - - FOLLOW TESTS - - -
    
    def test_follow(self):
        # Users
        u1 = {"username": "nammers1","email": "namn.namnsson@test.com","password": "namn123"}
        u2 = {"username": "nammers2","email": "namn.efernamn@test.com","password": "namn456"}
        # Register users
        rv_add_u1 = self.app.post('/users', data=json.dumps(u1), content_type='application/json')
        rv_add_u2 = self.app.post('/users', data=json.dumps(u2), content_type='application/json')
        # Login user 1
        rv_login_u1 = self.app.post('/login', data=json.dumps({"email": u1["email"], "password": u1["password"]}), content_type='application/json')
        acc_token_u1 = rv_login_u1.json["token_type"] + " " + rv_login_u1.json["access_token"]
        # User 1 follows user 2
        rv_u1_follows_u2 = self.app.post('/followed_users/' + u2["username"], headers={"Authorization": acc_token_u1})
        # Fetch all users followed by user 1
        rv1_u1_all_followers = self.app.get('/followed_users', headers={"Authorization": acc_token_u1})
        # Assert that user 2 is followed by user 1
        assert rv1_u1_all_followers.json["users"][0]["username"] == u2["username"]
    
    def test_follow_non_existent_user(self):
        # Users
        u1 = {"username": "nammers1","email": "namn.namnsson@test.com","password": "namn123"}
        # Register users
        rv_add_u1 = self.app.post('/users', data=json.dumps(u1), content_type='application/json')
        # Login user 1
        rv_login_u1 = self.app.post('/login', data=json.dumps({"email": u1["email"], "password": u1["password"]}), content_type='application/json')
        acc_token_u1 = rv_login_u1.json["token_type"] + " " + rv_login_u1.json["access_token"]
        # User 1 follows non existent user
        rv_u1_follows_non_existent = self.app.post('/followed_users/' + "nosuchuser", headers={"Authorization": acc_token_u1})
        # Assert that no user was found
        assert rv_u1_follows_non_existent.json["msg"] == "User does not exist"

    def test_unfollow(self):
        # Users
        u1 = {"username": "nammers1","email": "namn.namnsson@test.com","password": "namn123"}
        u2 = {"username": "nammers2","email": "namn.efernamn@test.com","password": "namn456"}
        # Register users
        rv_add_u1 = self.app.post('/users', data=json.dumps(u1), content_type='application/json')
        rv_add_u2 = self.app.post('/users', data=json.dumps(u2), content_type='application/json')
        # Login user 1
        rv_login_u1 = self.app.post('/login', data=json.dumps({"email": u1["email"], "password": u1["password"]}), content_type='application/json')
        acc_token_u1 = rv_login_u1.json["token_type"] + " " + rv_login_u1.json["access_token"]
        # User 1 follows user 2
        rv_u1_follows_u2 = self.app.post('/followed_users/' + u2["username"], headers={"Authorization": acc_token_u1})
        # User 1 unfollows user 2
        rv_u1_unfollows_u2 = self.app.delete('/followed_users/' + u2["username"], headers={"Authorization": acc_token_u1})
        # Fetch all users followed by user 1
        rv2_u1_all_followers = self.app.get('/followed_users', headers={"Authorization": acc_token_u1})
        # Assert that no users are followed by user 1
        assert rv2_u1_all_followers.json["users"] == []
    
    def test_unfollow_non_existent_user(self):
        # Users
        u1 = {"username": "nammers1","email": "namn.namnsson@test.com","password": "namn123"}
        # Register users
        rv_add_u1 = self.app.post('/users', data=json.dumps(u1), content_type='application/json')
        # Login user 1
        rv_login_u1 = self.app.post('/login', data=json.dumps({"email": u1["email"], "password": u1["password"]}), content_type='application/json')
        acc_token_u1 = rv_login_u1.json["token_type"] + " " + rv_login_u1.json["access_token"]
        # User 1 unfollows non existent user
        rv_u1_unfollows_non_existent = self.app.delete('/followed_users/' + "nosuchuser", headers={"Authorization": acc_token_u1})
        # Assert that no user was found
        assert rv_u1_unfollows_non_existent.json["msg"] == "User does not exist"
    
    # - - - USER TESTS - - -

    def test_get_all_users(self):
        # Users
        u1 = {"username": "nammers1","email": "namn.namnsson@test.com","password": "namn123"}
        u2 = {"username": "nammers2","email": "namn.efernamn@test.com","password": "namn456"}
        # Register Users
        rv_add_u1 = self.app.post('/users', data=json.dumps(u1), content_type='application/json')
        rv_add_u2 = self.app.post('/users', data=json.dumps(u2), content_type='application/json')
        # Login user 1
        rv_login_u1 = self.app.post('/login', data=json.dumps({"email": u1["email"], "password": u1["password"]}), content_type='application/json')
        acc_token_u1 = rv_login_u1.json["token_type"] + " " + rv_login_u1.json["access_token"]
        # User 1 follows user 2
        rv_u1_follows_u2 = self.app.post('/followed_users/' + u2["username"], headers={"Authorization": acc_token_u1})
        # Fetch the users followed by user 1
        rv_u1_users = self.app.get('/users', headers={"Authorization": acc_token_u1})
        # Assert that user 2 is in the list and is followed by user 1
        assert rv_u1_users.json["users"][0]["is_followed"] == "True"
    
    def test_get_single_user(self):
        # Users
        u1 = {"username": "nammers1","email": "namn.namnsson@test.com","password": "namn123"}
        u2 = {"username": "nammers2","email": "namn.efernamn@test.com","password": "namn456"}
        # Register Users
        rv_add_u1 = self.app.post('/users', data=json.dumps(u1), content_type='application/json')
        rv_add_u2 = self.app.post('/users', data=json.dumps(u2), content_type='application/json')
        # Login user 1
        rv_login_u1 = self.app.post('/login', data=json.dumps({"email": u1["email"], "password": u1["password"]}), content_type='application/json')
        acc_token_u1 = rv_login_u1.json["token_type"] + " " + rv_login_u1.json["access_token"]
        # User 1 follows user 2
        rv_u1_follows_u2 = self.app.post('/followed_users/' + u2["username"], headers={"Authorization": acc_token_u1})
        # Fetch user 2 using user 1
        rv_u1_user2 = self.app.get('/users/' + u2["username"], headers={"Authorization": acc_token_u1})
        # Assert that user 2 is in the response and is followed by user 1
        assert rv_u1_user2.json["is_followed"] == "True"
    
    def test_get_non_existent_user(self):
        # Users
        u1 = {"username": "nammers1","email": "namn.namnsson@test.com","password": "namn123"}
        # Register Users
        rv_add_u1 = self.app.post('/users', data=json.dumps(u1), content_type='application/json')
        # Login user 1
        rv_login_u1 = self.app.post('/login', data=json.dumps({"email": u1["email"], "password": u1["password"]}), content_type='application/json')
        acc_token_u1 = rv_login_u1.json["token_type"] + " " + rv_login_u1.json["access_token"]
        # Fetch non existing user
        rv_u1_user2 = self.app.get('/users/' + "nosuchuser", headers={"Authorization": acc_token_u1})
        # Assert that no user was found
        assert rv_u1_user2.json["msg"] == "User does not exist"
    
    # - - - QUESTION TESTS - - -

    def test_ask_question(self):
        # Users
        u1 = {"username": "nammers1","email": "namn.namnsson@test.com","password": "namn123"}
        # Register users
        rv_add_u1 = self.app.post('/users', data=json.dumps(u1), content_type='application/json')
        # Login Users
        rv_login_u1 = self.app.post('/login', data=json.dumps({"email": u1["email"], "password": u1["password"]}), content_type='application/json')
        acc_token_u1 = rv_login_u1.json["token_type"] + " " + rv_login_u1.json["access_token"]
        # User 1 asks a question
        q1 = {"question_title": "How do i make nice application?","question_body": "Hello I would very much like to make a nice application for this excellent course, pls help.", "course_room": "TDDD80"}
        rv_u1_asked_question = self.app.post('/questions', data=json.dumps(q1), content_type='application/json', headers={"Authorization": acc_token_u1})
        # Assert that the question posting was successful
        assert rv_u1_asked_question.json["msg"] == "Question successfully added"
    
    def test_ask_question_non_existent_course(self):
        # Users
        u1 = {"username": "nammers1","email": "namn.namnsson@test.com","password": "namn123"}
        # Register users
        rv_add_u1 = self.app.post('/users', data=json.dumps(u1), content_type='application/json')
        # Login Users
        rv_login_u1 = self.app.post('/login', data=json.dumps({"email": u1["email"], "password": u1["password"]}), content_type='application/json')
        acc_token_u1 = rv_login_u1.json["token_type"] + " " + rv_login_u1.json["access_token"]
        # User 1 asks a question
        q1 = {"question_title": "How do i make nice application?","question_body": "Hello I would very much like to make a nice application for this excellent course, pls help.", "course_room": "nosuchcourse"}
        rv_u1_asked_question = self.app.post('/questions', data=json.dumps(q1), content_type='application/json', headers={"Authorization": acc_token_u1})
        # Assert that the question posting failed
        assert rv_u1_asked_question.json["msg"] == "This course does not exist"
    
    def test_get_questions_from_followed_users(self):
        # Users
        u1 = {"username": "nammers1","email": "namn.namnsson@test.com","password": "namn123"}
        u2 = {"username": "nammers2","email": "namn.efernamn@test.com","password": "namn456"}
        # Register users
        rv_add_u1 = self.app.post('/users', data=json.dumps(u1), content_type='application/json')
        rv_add_u2 = self.app.post('/users', data=json.dumps(u2), content_type='application/json')
        # Login Users
        rv_login_u1 = self.app.post('/login', data=json.dumps({"email": u1["email"], "password": u1["password"]}), content_type='application/json')
        acc_token_u1 = rv_login_u1.json["token_type"] + " " + rv_login_u1.json["access_token"]
        rv_login_u2 = self.app.post('/login', data=json.dumps({"email": u2["email"], "password": u2["password"]}), content_type='application/json')
        acc_token_u2 = rv_login_u2.json["token_type"] + " " + rv_login_u2.json["access_token"]
        # User 2 asks a question
        q2 = {"question_title": "How do i make nice application?","question_body": "Hello I would very much like to make a nice application for this excellent course, pls help.", "course_room": "TDDD80"}
        rv_u2_asked_question = self.app.post('/questions', data=json.dumps(q2), content_type='application/json', headers={"Authorization": acc_token_u2})
        # User 1 follows user 2
        rv_u1_follows_u2 = self.app.post('/followed_users/' + u2["username"], headers={"Authorization": acc_token_u1})
        # Fetch the questions from users followed by user 1
        rv_get_questions = self.app.get('/questions', headers={"Authorization": acc_token_u1})
        # Assert that the question asked by user 2 was returned
        assert rv_get_questions.json["questions"][0]["author"]["email"] == u2["email"]
    
    def test_get_question_by_id(self):
        # Users
        u1 = {"username": "nammers1","email": "namn.namnsson@test.com","password": "namn123"}
        # Register users
        rv_add_u1 = self.app.post('/users', data=json.dumps(u1), content_type='application/json')
        # Login Users
        rv_login_u1 = self.app.post('/login', data=json.dumps({"email": u1["email"], "password": u1["password"]}), content_type='application/json')
        acc_token_u1 = rv_login_u1.json["token_type"] + " " + rv_login_u1.json["access_token"]
        # User 1 asks a question
        q1 = {"question_title": "How do i make nice application?","question_body": "Hello I would very much like to make a nice application for this excellent course, pls help.", "course_room": "TDDD80"}
        rv_u1_asked_question = self.app.post('/questions', data=json.dumps(q1), content_type='application/json', headers={"Authorization": acc_token_u1})
        # Fetch the questions with id 1
        rv_get_questions = self.app.get('/questions/1', headers={"Authorization": acc_token_u1})
        # Assert that the question asked by user 1 was returned
        assert rv_get_questions.json["author"]["email"] == u1["email"]
    
    def test_get_non_existent_question_by_id(self):
        # Users
        u1 = {"username": "nammers1","email": "namn.namnsson@test.com","password": "namn123"}
        # Register users
        rv_add_u1 = self.app.post('/users', data=json.dumps(u1), content_type='application/json')
        # Login Users
        rv_login_u1 = self.app.post('/login', data=json.dumps({"email": u1["email"], "password": u1["password"]}), content_type='application/json')
        acc_token_u1 = rv_login_u1.json["token_type"] + " " + rv_login_u1.json["access_token"]
        # Fetch the questions with id 1
        rv_get_questions = self.app.get('/questions/1', headers={"Authorization": acc_token_u1})
        # Assert that no question was found
        assert rv_get_questions.json["msg"] == "Question does not exist"
    
    def test_like_question(self):
        # Users
        u1 = {"username": "nammers1","email": "namn.namnsson@test.com","password": "namn123"}
        # Register Users
        rv_add_u1 = self.app.post('/users', data=json.dumps(u1), content_type='application/json')
        # Login user 1
        rv_login_u1 = self.app.post('/login', data=json.dumps({"email": u1["email"], "password": u1["password"]}), content_type='application/json')
        acc_token_u1 = rv_login_u1.json["token_type"] + " " + rv_login_u1.json["access_token"]
        # User 1 asks a question
        q1 = {"question_title": "How do i make nice application?","question_body": "Hello I would very much like to make a nice application for this excellent course, pls help.", "course_room": "TDDD80"}
        rv_u1_asked_question = self.app.post('/questions', data=json.dumps(q1), content_type='application/json', headers={"Authorization": acc_token_u1})
        # User 1 likes question 1
        rv_u1_like_p1 = self.app.post('/liked_questions/1', headers={"Authorization": acc_token_u1})
        # Assert that the like was successful
        assert rv_u1_like_p1.json["msg"] == "Like successful"
    
    def test_like_non_existent_question(self):
        # Users
        u1 = {"username": "nammers1","email": "namn.namnsson@test.com","password": "namn123"}
        # Register Users
        rv_add_u1 = self.app.post('/users', data=json.dumps(u1), content_type='application/json')
        # Login user 1
        rv_login_u1 = self.app.post('/login', data=json.dumps({"email": u1["email"], "password": u1["password"]}), content_type='application/json')
        acc_token_u1 = rv_login_u1.json["token_type"] + " " + rv_login_u1.json["access_token"]
        # User 1 likes non existent question
        rv_u1_like_p1 = self.app.post('/liked_questions/1', headers={"Authorization": acc_token_u1})
        # Assert that the like failed
        assert rv_u1_like_p1.json["msg"] == "Question does not exist"
    
    def test_unlike_question(self):
        # Users
        u1 = {"username": "nammers1","email": "namn.namnsson@test.com","password": "namn123"}
        # Register Users
        rv_add_u1 = self.app.post('/users', data=json.dumps(u1), content_type='application/json')
        # Login user 1
        rv_login_u1 = self.app.post('/login', data=json.dumps({"email": u1["email"], "password": u1["password"]}), content_type='application/json')
        acc_token_u1 = rv_login_u1.json["token_type"] + " " + rv_login_u1.json["access_token"]
        # User 1 asks a question
        q1 = {"question_title": "How do i make nice application?","question_body": "Hello I would very much like to make a nice application for this excellent course, pls help.", "course_room": "TDDD80"}
        rv_u1_asked_question = self.app.post('/questions', data=json.dumps(q1), content_type='application/json', headers={"Authorization": acc_token_u1})
        # User 1 unlikes post 1
        rv_u1_unlike_p1 = self.app.delete('/liked_questions/1', headers={"Authorization": acc_token_u1})
        # Assert that the unlike was successful
        assert rv_u1_unlike_p1.json["msg"] == "Unlike successful"
    
    def test_unlike_non_existent_question(self):
        # Users
        u1 = {"username": "nammers1","email": "namn.namnsson@test.com","password": "namn123"}
        # Register Users
        rv_add_u1 = self.app.post('/users', data=json.dumps(u1), content_type='application/json')
        # Login user 1
        rv_login_u1 = self.app.post('/login', data=json.dumps({"email": u1["email"], "password": u1["password"]}), content_type='application/json')
        acc_token_u1 = rv_login_u1.json["token_type"] + " " + rv_login_u1.json["access_token"]
        # User 1 unlikes non existent question
        rv_u1_unlike_p1 = self.app.delete('/liked_questions/1', headers={"Authorization": acc_token_u1})
        # Assert that the like failed
        assert rv_u1_unlike_p1.json["msg"] == "Question does not exist"
    
    # - - - ANSWER TESTS - - -

    def test_answer_question(self):
        # Users
        u1 = {"username": "nammers1","email": "namn.namnsson@test.com","password": "namn123"}
        # Register Users
        rv_add_u1 = self.app.post('/users', data=json.dumps(u1), content_type='application/json')
        # Login user 1
        rv_login_u1 = self.app.post('/login', data=json.dumps({"email": u1["email"], "password": u1["password"]}), content_type='application/json')
        acc_token_u1 = rv_login_u1.json["token_type"] + " " + rv_login_u1.json["access_token"]
        # User 1 asks a question
        q1 = {"question_title": "How do i make nice application?","question_body": "Hello I would very much like to make a nice application for this excellent course, pls help.", "course_room": "TDDD80"}
        rv_u1_asked_question = self.app.post('/questions', data=json.dumps(q1), content_type='application/json', headers={"Authorization": acc_token_u1})
        # User 1 answers question
        a1 = {"answer_body": "This is how you do it!"}
        rv_u1_answer_question = self.app.post('/answer_question/1', data=json.dumps(a1), content_type='application/json', headers={"Authorization": acc_token_u1})
        # Assert that question was answered successfully
        assert rv_u1_answer_question.json["msg"] == "Question successfully answered"
    
    def test_get_answers_to_question(self):
        # Users
        u1 = {"username": "nammers1","email": "namn.namnsson@test.com","password": "namn123"}
        # Register Users
        rv_add_u1 = self.app.post('/users', data=json.dumps(u1), content_type='application/json')
        # Login user 1
        rv_login_u1 = self.app.post('/login', data=json.dumps({"email": u1["email"], "password": u1["password"]}), content_type='application/json')
        acc_token_u1 = rv_login_u1.json["token_type"] + " " + rv_login_u1.json["access_token"]
        # User 1 asks a question
        q1 = {"question_title": "How do i make nice application?","question_body": "Hello I would very much like to make a nice application for this excellent course, pls help.", "course_room": "TDDD80"}
        rv_u1_asked_question = self.app.post('/questions', data=json.dumps(q1), content_type='application/json', headers={"Authorization": acc_token_u1})
        # User 1 answers question
        a1 = {"answer_body": "This is how you do it!"}
        rv_u1_answer_question = self.app.post('/answer_question/1', data=json.dumps(a1), content_type='application/json', headers={"Authorization": acc_token_u1})
        # Fetch answers to question 1
        rv_get_answers = self.app.get('/answers/1', headers={"Authorization": acc_token_u1})

        assert rv_get_answers.json["answers"][0]["author"]["email"] == u1["email"]
