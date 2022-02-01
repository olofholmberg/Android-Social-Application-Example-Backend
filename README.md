# REST API Backend for TDDD80 Project

This is a backend built in python using the Flask framework. The goal is to provide a fully functional backend for a social media Android application.

## Implemented REST API Routes and Android App Screen Mapping

| **Function** | **URL & Method** | **Request JSON Payload** | **App Screen** | **Auth** |
|:-------------------------:|:-------------------------:|:-------------------------:|:-------------------------:|:-------------------------:|
| Login as a user | /login [POST] | {"email":"email@test.com", "password":"pass123"} | Login Screen (MainActivity) | No |
| Logout as current user | /logout [POST] | - | Current User Profile Screen | Yes |
| Get a new access token | /refresh_token [POST] | - | No Screen (Should always be called when app is re-opened) | Yes |
| Get a list of all other users | /users [GET] | - | Users Screen | Yes |
| Register a user | /users [POST] | {"email":"email@test.com", "password":"pass123", "username":"uname"} | Register Screen | No |
| Get a single user | /users/&lt;username&gt; [GET] | - | Other User Profile Screen | Yes |
| Get a list of currently followed users | /followed_users [GET] | - | Followed Users Screen | Yes |
| Follow another user | /followed_users/&lt;username&gt; [POST] | - | All screens where other users are shown | Yes |
| Unfollow a followed user | /followed_users/&lt;username&gt; [DELETE] | - | All screens where other users are shown | Yes |
| Get a list of all followed user questions | /questions [GET] | - | Home Screen | Yes |
| Ask a question | /questions [POST] | {"question_title":"My Question", "question_body":"My Longer Question", "course_room":"TDDD80"} | Ask A Question Screen | Yes |
| Get a question and its answers | /questions/&lt;question_id&gt; [GET] | - | Question Details Screen | Yes |
| Like a question | /liked_questions/&lt;id&gt; [POST] | - | All screens where questions are shown | Yes |
| Unlike a liked question | /liked_questions/&lt;id&gt; [DELETE] | - | All screens where questions are shown | Yes |
| Answer a question | /answer_question/&lt;question_id&gt; [POST] | {"answer_body":"My Answer"} | Answer A Question Screen | Yes |
| Get the answers for a question | /answers/&lt;question_id&gt; [GET] | - | Currently No Screen | Yes |

- All successes where JSON data is requested are returned with only the requested data unless there is an error.
- All other successes where JSON data is not requested are returned with the following: {"success":"This is what succeeded"}, to be used for toasts and changing UI elements.
- All errors are returned with the JSON data {"msg":"This is the error"}, to be used for toasts and changing UI elements.

## Python virtual environment

### Creation

The virtual environment should be created by running the following in the backend project directory:

```
$ python -m venv venv
```

### Activation

To activate your venv when using *Windows*:

```
$ venv\Scripts\Activate
```

To activate your venv when using *Linux*:

```
$ source venv/bin/activate
```

### Flask installation

Activate your virtual environment and then install Flask:

```
(venv) $ pip install flask
```

## Web Application

### Creating the application

Create the app directory:

```
(venv) $ mkdir app
```

Create the following files:

1. app/__init.py
2. app/routes.py
3. wsgi.py (this is the main application module)

### Import the app into Flask

To import your application when using *Windows*:

```
(venv) $ set FLASK_APP=wsgi.py
```

To import your application when using *Linux*:

```
(venv) $ export FLASK_APP=wsgi.py
```

**IMPORTANT:**

If you do not want having to repeatedly import the application each time you switch terminal sessions you can use the *python-dotenv* package. Install the package in your venv:

```
(venv) $ pip install python-dotenv
```

Create .flaskenv in the project root directory with the following contents:

```python
FLASK_APP=wsgi.py
```

The .flaskenv file can also hold other environment variables that you might want or need.

### Run the application

```
(venv) $ flask run
```

If the running of the application is successful it should be possible to access the application via [your localhost.](http://localhost:5000/)

## Create the Config class

Create config.py in the base directory. This file will store configuration options for Flask.

Access these by importing app and use their assigned name:

```python
from app import app
app.config['JWT_SECRET_KEY']
```

## Changing the port

Depending on how the application is started the port is set in different locations. If running:

```
(venv) $ python wsgi.py
```

The port declared in wsgi.py is used. If running:

```
(venv) $ flask run
```

Then the port declared in .flaskenv is used.

# Creating and managing the database

First install SQLAlchemy:

```
(venv) $ pip install flask-sqlalchemy
```

Then to ease the updating and changing of the database install Flask-Migrate:

```
(venv) $ pip install flask-migrate
```

## Enabling Repository Migration

Create the migration repository:

```
(venv) $ flask db init
```

After that proceed to do the first migration:

```
(venv) $ flask db migrate -m "users table"
```

To apply the migration the database has to be upgraded:

```
(venv) $ flask db upgrade
```

The database can also be reverted to the previous migration using downgrade.

## Database Workflow

The workflow for the database is as follows:

1. Modify models.py
2. Run: *(venv) $ flask db migrate -m "my migrate message here"*
3. Run: *(venv) $ flask db upgrade*
4. Start python
5. Run: >>> from app import db_manager
6. Run: >>> db_manager.init_db()
4. Add migration script to git and commit

If needed, run: *(venv) $ flask db downgrade* to undo latest migration.

## Testing the application using requests

Start the application with:

```
(venv) $ flask run
```

Then using another terminal, start the venv and python. Then run:

```python
>>> import requests, json
>>> resp = requests.post('http://127.0.0.1:5090/users', json={"username": "unamn", "email": "unamn@mail.com", "password": "namn123"})
>>> resp2 = requests.post('http://127.0.0.1:5090/login', json={"email": "unamn@mail.com", "password": "namn123"})
>>> json2 = json.loads(resp2.text)
>>> auth_header_content = json2['token_type'] + ' ' + json2['access_token']
>>> resp3 = requests.get('http://127.0.0.1:5090/secretroute', headers={'Authorization': auth_header_content})
```

## Unittesting of the application

Install the prerequisites for unittesting:

1. Run: *(venv) $ pip install pytest*
2. Run: *(venv) $ pip install coverage*

Then to run the unittests without coverage:

```
(venv) $ pytest unit_tests.py
```

To run the unittests with coverage (add rP flag to allow printing):

```
(venv) $ coverage run -m pytest unit_tests.py -rP
```

To present the coverage of the application code, run (omit the venv directory to get a better coverage estimation):

```
(venv) $ coverage html --omit="*/venv/*"
```

## JWT Login

To hide the JWT secret from source code (export on linux):

```
(venv) $ set SERVER_SECRET='my-secret-code'
```

In config.py:

```python
JWT_SECRET_KEY = os.environ.get('SERVER_SECRET') or 'not-super-secret'
```

When token is expired a 401 is sent with text: {"msg":"Token has expired"}
When token is manually revoked by logout a 401 is sent with text: {"msg":"Token has been revoked"}

## Deploying on Heroku

Install gunicorn and psycopg2, then update requirements.txt:

```
(venv) $ pip install gunicorn
(venv) $ pip install psycopg2
(venv) $ pip freeze > requirements.txt
```

First install the Heroku CLI, and whe installed run:

```
$ heroku login
```

To create your application run:

```
$ heroku apps:create <your app name>
```

To add a database to your application run:

```
$ heroku addons:add heroku-postgresql:hobby-dev
```

Add a procfile to your project with the following contents:

```
web: flask db upgrade; gunicorn <your app name>:app
```

Set the necessary environment variables:

```
$ heroku config:set FLASK_APP=wsgi.py
$ heroku config:set SERVER_SECRET=<your server secret>
```

Push to Heroku master:

```
$ git push heroku master
```

Possible causes for application crash (Heroku error code H10):

1. Procfile error
2. Manually setting ports
3. Missing environment variables
4. Missing required scripts

