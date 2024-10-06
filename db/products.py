import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# חיבור למסד הנתונים
def connect_db():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
    return conn

# פונקציה להוספת או עדכון מוצר
def add_or_update_product(product_name, quantity, user_id):
    conn = connect_db()
    cursor = conn.cursor()

    try:
        # חיפוש מוצר לפי שם ו-user_id
        cursor.execute("SELECT quantity FROM products WHERE name = %s AND user_id = %s", (product_name, user_id))
        result = cursor.fetchone()

        if result:
            # עדכון כמות מוצר קיים
            new_quantity = result[0] + quantity
            cursor.execute("UPDATE products SET quantity = %s WHERE name = %s AND user_id = %s", (new_quantity, product_name, user_id))
            message = f"Updated {product_name}, new quantity: {new_quantity}"
        else:
            # הוספת מוצר חדש
            cursor.execute("INSERT INTO products (name, quantity, user_id) VALUES (%s, %s, %s)", (product_name, quantity, user_id))
            message = f"Added new product: {product_name}, quantity: {quantity}"

        conn.commit()

        # שליפת כל המוצרים הקשורים ל-user_id
        cursor.execute("SELECT name, quantity FROM products WHERE user_id = %s", (user_id,))
        products = cursor.fetchall()
        products_dict = {name: quantity for name, quantity in products}

        return message, products_dict

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        cursor.close()
        conn.close()

# פונקציה למחיקת מוצר
def delete_product(product_name, user_id):
    conn = connect_db()
    cursor = conn.cursor()

    try:
        # מחיקת מוצר לפי שם ו-user_id
        cursor.execute("DELETE FROM products WHERE name = %s AND user_id = %s", (product_name, user_id))
        conn.commit()

        # שליפת כל המוצרים הקשורים ל-user_id
        cursor.execute("SELECT name, quantity FROM products WHERE user_id = %s", (user_id,))
        products = cursor.fetchall()
        products_dict = {name: quantity for name, quantity in products}

        return f"Deleted {product_name}", products_dict

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        cursor.close()
        conn.close()

# פונקציה למחיקת כל המוצרים
def delete_all_products(user_id):
    conn = connect_db()
    cursor = conn.cursor()

    try:
        # מחיקת כל המוצרים הקשורים ל-user_id
        cursor.execute("DELETE FROM products WHERE user_id = %s", (user_id,))
        conn.commit()

        return "All products deleted", {}

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        cursor.close()
        conn.close()

# פונקציה להחזרת כל המוצרים
def get_all_products(user_id):
    conn = connect_db()
    cursor = conn.cursor()

    try:
        # שליפת כל המוצרים הקשורים ל-user_id
        cursor.execute("SELECT name, quantity FROM products WHERE user_id = %s", (user_id,))
        products = cursor.fetchall()
        products_dict = {name: quantity for name, quantity in products}
        return products_dict

    except Exception as e:
        raise e

    finally:
        cursor.close()
        conn.close()
