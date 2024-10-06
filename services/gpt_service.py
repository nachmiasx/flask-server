import openai
import os
from flask import jsonify
import json
import re
from dotenv import load_dotenv
from collections import defaultdict
from db.products import add_or_update_product  

load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')

def summarize_receipt(text, user_id):
    try:
        print("Starting GPT-3 analysis...") 
        print(f"Received text for analysis: {text[:100]}...")  

        prompt = (
            "Please summarize the following receipt and extract items (word) and quantities in the following format:\n"
            "item : quantity\n"
            "If you see any decimal numbers, ignore them and use 1 as the default quantity.\n" + text
        )
        print(f"Prompt sent to GPT-3: {prompt[:100]}...") 

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a receipt summarizer."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.5,
        )
        
        print(f"Full GPT-3 response: {json.dumps(response, indent=2)}")

        if not response or not response.choices:
            print("No response or choices received from GPT-3.")  
            return jsonify({"error": "No response received from GPT-3"}), 500
        
        content = response.choices[0].message['content'].strip()
        print(f"GPT-3 response received: {content[:100]}...")  

        # חילוץ הפריטים והכמויות
        items = parse_receipt_content(content)
        print(f"Extracted items: {items}")  

        # שמירת המידע במסד הנתונים
        for product_name, quantity in items.items():
            add_or_update_product(product_name, quantity, user_id)  

        return jsonify({"message": "Products saved successfully", "products": items}), 200

    except Exception as e:
        print(f"Unexpected error occurred: {str(e)}")  
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


def parse_receipt_content(content):
    print(f"Parsing content: {content[:100]}...") 
    items = defaultdict(int) 
    lines = content.split("\n")
    for line in lines:
        parts = line.split(":")
        print(f"Processing line: {line}") 
        if len(parts) == 2:
            item = parts[0].strip()
            quantity_str = parts[1].strip()

           
            numeric_quantity = re.sub(r'[^0-9]', '', quantity_str)

            try:
                quantity = int(numeric_quantity) if numeric_quantity else 1  
                if not re.match(r'\d+|\d+\.\d+|\d{12,13}', item):  
                    items[item] += quantity
                    print(f"Added item: {item}, quantity: {quantity}")  
                else:
                    print(f"Skipping line (item appears to be a code/price): {line}")
            except ValueError:
                print(f"Failed to parse quantity from line: {line}")
        else:
            print(f"Skipping line (does not contain item:quantity format): {line}")
    
    return dict(items)
