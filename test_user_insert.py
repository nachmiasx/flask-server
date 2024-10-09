import os
import pytest
from flask import Flask
# from SQLAlchemy import *
from app import app as flask_app, db  # Import your app and db
from db.users import User
from db.question_answers import QuestionAnswer

# Set the testing configuration
TEST_DATABASE_URI = os.getenv('TEST_DATABASE_URL',
                              'postgresql://username:password@localhost/test_db')  # Update this line with your actual test DB


@pytest.fixture
def app():
    # Create a new app instance for testing
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = TEST_DATABASE_URI
    flask_app.config['TESTING'] = True
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Create the database tables
    with flask_app.app_context():
        db.create_all()

    yield flask_app

    # Clean up the database
    with flask_app.app_context():
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_signup(client):
    response = client.post('/signup', data={
        'email': 'testuser@example.com',
        'password': 'TestPassword123!'
    })
    assert response.status_code == 302  # Check for redirect
    assert b'Sign in here' in response.data  # Check for sign-in prompt


def test_login(client):
    # First sign up a user
    client.post('/signup', data={
        'email': 'testuser@example.com',
        'password': 'TestPassword123!'
    })

    # Now try to log in
    response = client.post('/login', data={
        'email': 'testuser@example.com',
        'pass': 'TestPassword123!'
    })
    assert response.status_code == 200
    assert b"token" in response.data  # Check if token is present in the response


def test_ask_question(client):
    # First sign up and log in a user
    client.post('/signup', data={
        'email': 'testuser@example.com',
        'password': 'TestPassword123!'
    })
    login_response = client.post('/login', data={
        'email': 'testuser@example.com',
        'pass': 'TestPassword123!'
    })

    token = login_response.get_json()['token']

    # Now ask a question
    response = client.post('/ask', json={
        'question': 'What is the capital of France?'
    }, headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == 200
    assert b"question" in response.data  # Adjust this based on your actual response structure

