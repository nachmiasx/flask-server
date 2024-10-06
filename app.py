from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from db.products import add_or_update_product, get_all_products, delete_product, delete_all_products
from db.users import save_user, login_user
from services.vision_service import analyze_image
from services.gpt_service import summarize_receipt
import jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

SECRET_KEY = os.getenv('SECRET_KEY')  

# פונקציה ליצירת JWT
def create_jwt(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=1)  # תוקף של שעה
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

# פונקציה לאימות JWT
def verify_jwt(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None  # הטוקן פג תוקף
    except jwt.InvalidTokenError:
        return None  # הטוקן לא תקין

@app.route('/')
def serve_react_app():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_react_paths(path):
    return send_from_directory(app.static_folder, 'index.html')

# נתיב לרישום משתמש חדש
@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400

    try:
        save_user(email, password)
        return jsonify({"message": "User signed up successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# נתיב להתחברות משתמש
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400

    if login_user(email, password):
        # יצירת JWT
        token = create_jwt(email)
        return jsonify({"message": "Login successful", "token": token}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401

# נתיב להוספה או עדכון מוצר
@app.route('/products/update', methods=['POST'])
def update_product():
    token = request.headers.get('Authorization')
    user_data = verify_jwt(token.split()[1]) if token else None
    if not user_data:
        return jsonify({"error": "Unauthorized"}), 401

    user_id = user_data['user_id']
    data = request.json
    product_name = data.get('name')
    quantity = data.get('quantity')

    if not product_name or quantity is None:
        return jsonify({"error": "Missing product name or quantity"}), 400

    try:
        message, products = add_or_update_product(product_name, quantity, user_id)
        return jsonify({"message": message, "products": products}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# נתיב למחיקת מוצר
@app.route('/products/delete/<string:product_name>', methods=['DELETE'])
def delete_product_route(product_name):
    token = request.headers.get('Authorization')
    user_data = verify_jwt(token.split()[1]) if token else None
    if not user_data:
        return jsonify({"error": "Unauthorized"}), 401

    user_id = user_data['user_id']
    try:
        print(f"Product to delete: {product_name}")  # הדפסת שם המוצר לבדיקה
        message, products = delete_product(product_name, user_id)
        return jsonify({"message": message, "products": products}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# נתיב למחיקת כל המוצרים
@app.route('/products/delete-all', methods=['DELETE'])
def delete_all_products_route():
    token = request.headers.get('Authorization')
    user_data = verify_jwt(token.split()[1]) if token else None
    if not user_data:
        return jsonify({"error": "Unauthorized"}), 401

    user_id = user_data['user_id']
    try:
        message, products = delete_all_products(user_id)
        return jsonify({"message": message, "products": products}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# נתיב להצגת כל המוצרים
@app.route('/products', methods=['GET'])
def list_products():
    token = request.headers.get('Authorization')
    user_data = verify_jwt(token.split()[1]) if token else None
    if not user_data:
        return jsonify({"error": "Unauthorized"}), 401

    user_id = user_data['user_id']
    try:
        products = get_all_products(user_id)
        return jsonify({"products": products}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# נתיב לניתוח תמונה באמצעות Google Vision API
@app.route('/analyze-image', methods=['POST'])
def analyze_image_route():
    token = request.headers.get('Authorization')
    user_data = verify_jwt(token.split()[1]) if token else None
    if not user_data:
        return jsonify({"error": "Unauthorized"}), 401

    user_id = user_data['user_id']

    data = request.json
    if 'image' not in data:
        return jsonify({"error": "Image not provided"}), 400

    vision_response, status_code = analyze_image(data['image'])

    if status_code != 200:
        return vision_response, status_code

    extracted_text = vision_response.get_json().get('texts')
    
    # העברת user_id לפונקציה summarize_receipt
    response = summarize_receipt(extracted_text, user_id)
    
    return response




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
