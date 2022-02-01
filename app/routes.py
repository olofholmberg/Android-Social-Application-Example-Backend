from flask import request, jsonify
from app import app, db_manager, jwt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

# - - - Index Route - - -

@app.route('/')
@app.route('/index')
def index():
    return "Hi there!"


# - - - Authentication routes (login, logout, token etc.) - - -

# Helper required for JWT functionality
@jwt.token_in_blacklist_loader
def check_if_token_revoked(decoded_token):
    return db_manager.is_token_revoked(decoded_token)


# Returns an access token for a successful login using the provided email and
# password.
@app.route('/login', methods=['POST'])
def login():
    email = request.json.get('email', None)
    password = request.json.get('password', None)
    user = db_manager.get_user_by_email(email)
    if not user:
        return jsonify({"msg": "Wrong email"}), 409
    if not user.check_password(password):
        return jsonify({"msg": "Wrong password"}), 409
    access_token = create_access_token(identity=email)
    return jsonify({
        "access_token": access_token,
        "token_type": "Bearer",
        "expires_in": int(app.config['JWT_ACCESS_TOKEN_EXPIRES'].total_seconds())
    }), 201


# Adds the provided access token to the blacklist.
@app.route('/logout', methods=['POST'])
@jwt_required
def logout():
    auth_header = request.headers.get('Authorization')
    revoked_token = auth_header.split(" ")[1]
    db_manager.add_token_to_blacklist(revoked_token, app.config['JWT_IDENTITY_CLAIM'])
    return jsonify({"msg": "Logout successful"}), 201


# Adds the provided access token to the blacklist and also creates a new
# access token for the requesting user.
@app.route('/refresh_token', methods=['POST'])
@jwt_required
def refresh_token():
    auth_header = request.headers.get('Authorization')
    revoked_token = auth_header.split(" ")[1]
    db_manager.add_token_to_blacklist(revoked_token, app.config['JWT_IDENTITY_CLAIM'])
    email = get_jwt_identity()
    access_token = create_access_token(identity=email)
    return jsonify({
        "access_token": access_token,
        "token_type": "Bearer",
        "expires_in": int(app.config['JWT_ACCESS_TOKEN_EXPIRES'].total_seconds())
    }), 201


# - - - User routes (registering, fetching etc.) - - -

# Fetches all users except the one making the request and also whether they
# are followed or not by the requesting user.
@app.route('/users')
@jwt_required
def all_users():
    email = get_jwt_identity()
    current_user = db_manager.get_user_by_email(email)
    users = []
    for user in db_manager.get_all_users(current_user):
        user_dict = user.to_dict()
        user_dict["is_followed"] = "{}".format(current_user.is_following(user))
        users.append(user_dict)
    return jsonify({"users": users})


# Registers a new user to the application, the username and email address
# must be unique.
@app.route('/users', methods=['POST'])
def register():
    email = request.json.get('email', None)
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    user = db_manager.get_user_by_username(username)
    if user is not None:
        return jsonify({"msg": "Username is already taken"}), 303
    user = db_manager.get_user_by_email(email)
    if user is not None:
        return jsonify({"msg": "Email is already registered"}), 303
    db_manager.register_user(username, email, password)
    return jsonify({"msg": "User successfully registered"})


# Fetches user details based on the provided username.
@app.route('/users/<username>')
@jwt_required
def user_by_username(username):
    email = get_jwt_identity()
    current_user = db_manager.get_user_by_email(email)
    fetched_user = db_manager.get_user_by_username(username)
    if fetched_user is None:
        return jsonify({"msg": "User does not exist"}), 303
    fetched_user_dict = fetched_user.to_dict()
    fetched_user_dict["is_followed"] = "{}".format(current_user.is_following(fetched_user))
    return jsonify(fetched_user_dict)


# Fetches user details based on the current user.
@app.route('/users/current')
@jwt_required
def current_user():
    email = get_jwt_identity()
    current_user = db_manager.get_user_by_email(email)
    current_user_dict = current_user.to_dict()
    return jsonify(current_user_dict)


# - - - Follow routes (follow, unfollow etc.) - - -

# Gets all the users that are followed by the requesting user.
@app.route('/followed_users')
@jwt_required
def followed_users():
    email = get_jwt_identity()
    current_user = db_manager.get_user_by_email(email)
    followed_users = []
    for followed_user in db_manager.get_all_followed_users(current_user):
        user_dict = followed_user.to_dict()
        followed_users.append(user_dict)
    return jsonify({"users": followed_users})


# The requesting user follows the user with the provided username.
@app.route('/followed_users/<username>', methods=['POST'])
@jwt_required
def follow(username):
    email = get_jwt_identity()
    current_user = db_manager.get_user_by_email(email)
    user_to_follow = db_manager.get_user_by_username(username)
    if user_to_follow is None:
        return jsonify({"msg": "User does not exist"}), 303
    db_manager.add_follow_relationship(current_user, user_to_follow)
    return jsonify({"msg": "Follow successful"}), 200


# The requesting user unfollows the user with the provided username.
@app.route('/followed_users/<username>', methods=['DELETE'])
@jwt_required
def unfollow(username):
    email = get_jwt_identity()
    current_user = db_manager.get_user_by_email(email)
    user_to_unfollow = db_manager.get_user_by_username(username)
    if user_to_unfollow is None:
        return jsonify({"msg": "User does not exist"}), 303
    db_manager.remove_follow_relationship(current_user, user_to_unfollow)
    return jsonify({"msg": "Unfollow successful"}), 200


# - - - Question routes (ask question, fetch question, like question etc.) - - -

# Fetches the questions asked by users followed by the requesting user.
@app.route('/questions')
@jwt_required
def all_questions():
    email = get_jwt_identity()
    current_user = db_manager.get_user_by_email(email)
    questions = []
    for question in db_manager.get_followed_questions(current_user):
        question_dict = question.to_dict()
        question_dict["is_liking"] = "{}".format(current_user.is_liking_question(question))
        questions.append(question_dict)
    return jsonify({"questions": questions})


# Posts a question using the provided JSON data.
@app.route('/questions', methods=['POST'])
@jwt_required
def ask_question():
    question_title = request.json.get('question_title', None)
    question_body = request.json.get('question_body', None)
    course_room = request.json.get('course_room', None)
    email = get_jwt_identity()
    current_user = db_manager.get_user_by_email(email)
    current_course = db_manager.get_course_by_code(course_room)

    if not current_course:
        return jsonify({"msg": "This course does not exist"}), 404
    
    db_manager.add_question(question_title, question_body, current_user, current_course)
    return jsonify({"msg": "Question successfully added"}), 200


# Fetches the question with the provided question_id and the related answers.
@app.route('/questions/<question_id>')
@jwt_required
def get_question(question_id):
    email = get_jwt_identity()
    current_user = db_manager.get_user_by_email(email)
    current_question = db_manager.get_question_by_id(question_id)
    if current_question is None:
        return jsonify({"msg": "Question does not exist"}), 303
    current_question_dict = current_question.to_dict()
    current_question_dict["is_liking"] = "{}".format(current_user.is_liking_question(current_question))
    return jsonify(current_question_dict)


# The requesting user likes the question with the provided question_id.
@app.route('/liked_questions/<question_id>', methods=['POST'])
@jwt_required
def like_question(question_id):
    email = get_jwt_identity()
    current_user = db_manager.get_user_by_email(email)
    question_to_like = db_manager.get_question_by_id(question_id)
    if question_to_like is None:
        return jsonify({"msg": "Question does not exist"}), 303
    db_manager.like_question(current_user, question_to_like)
    return jsonify({"msg": "Like successful"}), 200


# The requesting user unlikes the question with the provided question_id.
@app.route('/liked_questions/<question_id>', methods=['DELETE'])
@jwt_required
def unlike_question(question_id):
    email = get_jwt_identity()
    current_user = db_manager.get_user_by_email(email)
    question_to_unlike = db_manager.get_question_by_id(question_id)
    if question_to_unlike is None:
        return jsonify({"msg": "Question does not exist"}), 303
    db_manager.unlike_question(current_user, question_to_unlike)
    return jsonify({"msg": "Unlike successful"}), 200


# Fetches the questions asked by users followed by the requesting user.
@app.route('/myquestions')
@jwt_required
def my_questions():
    email = get_jwt_identity()
    current_user = db_manager.get_user_by_email(email)
    questions = []
    for question in db_manager.get_questions_by_user(current_user):
        question_dict = question.to_dict()
        question_dict["is_liking"] = "{}".format(current_user.is_liking_question(question))
        questions.append(question_dict)
    return jsonify({"questions": questions})


# - - - Answer routes (answer question, like answer etc.) - - -

# Answer the question with the provided question_id.
@app.route('/answer_question/<question_id>', methods=['POST'])
@jwt_required
def answer_question(question_id):
    email = get_jwt_identity()
    current_user = db_manager.get_user_by_email(email)
    current_question = db_manager.get_question_by_id(question_id)
    if current_question is None:
        return jsonify({"msg": "Question does not exist"}), 303
    answer_body = request.json.get('answer_body', None)
    db_manager.add_answer(answer_body, current_user, current_question)
    return jsonify({"msg": "Question successfully answered"}), 200


# Fetch the answers for the question with the provided question_id.
@app.route('/answers/<question_id>')
@jwt_required
def get_question_answers(question_id):
    email = get_jwt_identity()
    current_user = db_manager.get_user_by_email(email)
    current_question = db_manager.get_question_by_id(question_id)
    if current_question is None:
        return jsonify({"msg": "Question does not exist"}), 303
    question_answers = []
    for answer in db_manager.get_question_answers(current_question):
        question_answers.append(answer.to_dict())
    return jsonify({"answers": question_answers})


# - - - Courses routes (fetch available courses etc.) - - -

# Fetch all available courses.
@app.route('/courses')
@jwt_required
def get_available_courses():
    email = get_jwt_identity()
    current_user = db_manager.get_user_by_email(email)
    courses = []
    for course in db_manager.get_all_courses():
        courses.append(course.to_dict())
    return jsonify({"courses": courses})

    email = get_jwt_identity()
    current_user = db_manager.get_user_by_email(email)
    questions = []
    for question in db_manager.get_followed_questions(current_user):
        question_dict = question.to_dict()
        question_dict["is_liking"] = "{}".format(current_user.is_liking_question(question))
        questions.append(question_dict)
    return jsonify({"questions": questions})