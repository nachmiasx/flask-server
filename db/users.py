import os
import bcrypt
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import logging


# Load environment variables
load_dotenv()

# Define the SQLAlchemy base class
Base = declarative_base()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class User(Base):
    __tablename__ = 'users'

    email = Column(String, primary_key=True)
    password_hash = Column(String)
    # Define the relationship with QuestionAnswer
    questions = relationship("QuestionAnswer", back_populates="user")


# Database connection setup
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_PORT = os.getenv('DB_PORT')

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)


# Function to hash password using bcrypt
def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


# Function to save a new user
def save_user(email, password):
    session = Session()

    hashed_password = hash_password(password)

    try:
        # Debug: Print the hashed password before saving
        logger.info(f"Hashed password: {hashed_password}")

        # Create a new User instance
        new_user = User(email=email, password_hash=hashed_password)

        # Add the user to the session and commit
        session.add(new_user)
        session.commit()
        logger.info("User saved successfully.")
    except Exception as e:
        logger.info(f"Error saving user: {e}")
        session.rollback()  # Rollback if there's an error
    finally:
        session.close()  # Close the session


# Function to login a user
def login_user(email, password):
    session = Session()
    try:
        user = session.query(User).filter_by(email=email).first()

        if user is None:
            logger.info("User does not exist.")
            return False

        stored_password = user.password_hash

        # Check if the hashed password matches the provided password
        if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
            logger.info("Login successful.")
            return True
        else:
            logger.info("Invalid password.")
            return False

    except Exception as e:
        logger.info(f"Error logging in: {e}")
        return False
    finally:
        session.close()  # Close the session
