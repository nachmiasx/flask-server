import base64
import io
from PIL import Image
from google.cloud import vision
from google.oauth2 import service_account
from flask import jsonify, request
import os
from google.oauth2 import service_account
from dotenv import load_dotenv

load_dotenv()


def get_credentials():
   
    key_path = os.getenv('GOOGLE_VISION_KEY_PATH')
    
    if not key_path:
        raise Exception("GOOGLE_VISION_KEY_PATH environment variable is not set")
    
    return service_account.Credentials.from_service_account_file(key_path)

# פונקציה לעיבוד התמונה עם Google Vision API
def analyze_image(base64_image):
    try:
        print("Starting image analysis...")  
       
        decoded_image_data = base64.b64decode(base64_image)
        print("Image decoded successfully.")  
        image = Image.open(io.BytesIO(decoded_image_data))
        print("Image opened successfully.")  

       
        byte_array = io.BytesIO()
        image.save(byte_array, format="PNG")
        byte_array = byte_array.getvalue()

        client = vision.ImageAnnotatorClient(credentials=get_credentials())
        image = vision.Image(content=byte_array)
        feature = vision.Feature(type_=vision.Feature.Type.TEXT_DETECTION)
        request = vision.AnnotateImageRequest(image=image, features=[feature])
        print("Request to Google Vision prepared.")  
        response = client.annotate_image(request)

        
        if response.error.message:
            print(f"Google Vision API error: {response.error.message}")
            return jsonify({"error": response.error.message}), 500

        
        detected_texts = "\n".join([text.description for text in response.text_annotations])
        print(f"Detected texts: {detected_texts[:50]}...")  
        return jsonify({"texts": detected_texts}), 200

    except Exception as e:
        print(f"Error occurred: {str(e)}") 
        return jsonify({"error": str(e)}), 500