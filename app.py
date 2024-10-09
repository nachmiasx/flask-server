from flask import Flask, request, jsonify, send_from_directory, redirect, url_for, render_template
from flask_cors import CORS
from services.gpt_service import new_question
from db.users import save_user, login_user
from db.question_answers import *
import jwt
from datetime import datetime, timedelta, time
import os
from dotenv import load_dotenv
import logging

load_dotenv()

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

SECRET_KEY = os.getenv('SECRET_KEY')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)



def create_jwt(user_id):
    creation_time = datetime.utcnow()
    expiration_time = creation_time + timedelta(hours=1)
    payload = {
        'email': user_id,
        'exp': expiration_time,
        'iat': creation_time
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    logger.info(f"Token created at: {creation_time}")
    logger.info(f"Token expires at: {expiration_time}")
    logger.info(f"Token: {token}")
    return token

def verify_jwt(token):
    verification_time = datetime.utcnow()
    logger.info(f"Token verification time: {verification_time}")
    logger.info(f"Token: {token}")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        logger.info(f"Token successfully verified. Payload: {payload}")
        return payload
    except jwt.ExpiredSignatureError:
        logger.error("Token has expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.error(f"Invalid token: {str(e)}")
        return None


@app.route('/')
def login_page():
    return render_template('login.html')

@app.route('/signup')
def signup_page():
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup():
    data = request.form
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400

    try:
        save_user(email, password)
        # Redirect to login page after successful signup
        return redirect(url_for('login_page'))  # Redirect to the login page
    except Exception as e:
        return render_template('signup.html', error=str(e))  # Show error on the signup page


@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('pass')

    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400

    if login_user(email, password):
        logger.info(f"Logged in as {email}")
        token = create_jwt(email)
        logger.info("User with email:" + email + " logged in")
        return jsonify({"token": token, "redirect": url_for('ask_page')}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401

@app.route('/ask')
def ask_page():
    return render_template('ask.html')


@app.route('/ask', methods=['POST'])
def ask():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "Authorization token is missing"}), 401
    token = token.split(" ")[1]
    user = verify_jwt(token)
    if not user:
        return jsonify({"error": "Invalid or expired token"}), 401

    if request.is_json:
        data = request.get_json()
        question = data.get('question')

        if not question:
            return jsonify({"error": "Question not provided"}), 400
        try:
            answer = new_question(question)
            email = user['email']
            save_question_answer(email=email, question=question, answer=answer)

            return jsonify({"question": question, "answer": answer}), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Request must be JSON"}), 400

@app.route('/ask/history', methods=['GET'])
def get_history():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "Authorization token is missing"}), 401
    token = token.split(" ")[1]
    user = verify_jwt(token)
    if not user:
        return jsonify({"error": "Invalid or expired token"}), 401

    try:
        email = user['email']
        question_history = get_question_history(email)
        return jsonify({"history": question_history}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
