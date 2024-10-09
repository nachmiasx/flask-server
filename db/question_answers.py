import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, JSON
from sqlalchemy.orm import sessionmaker, relationship
from db.users import User, Base
import logging

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# QuestionAnswer table definition
class QuestionAnswer(Base):
    __tablename__ = 'question_answers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    question = Column(String, nullable=False)
    answer = Column(String, nullable=False)  # Store the answer as JSON
    email = Column(String, ForeignKey('users.email'), nullable=False)

    # Define the relationship back to the User
    user = relationship("User", back_populates="questions")


# Database connection setup
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_PORT = os.getenv('DB_PORT')

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# Function to save a question and answer for a user
def save_question_answer(email, question, answer):
    session = Session()

    try:
        user = session.query(User).filter_by(email=email).first()
        if not user:
            logger.error(f"User with email {email} does not exist.")
            return False
        new_qa = QuestionAnswer(question=question, answer=answer, email=email)
        session.add(new_qa)
        session.commit()
        logger.info(f"Question and answer saved successfully for user: {email}")
        return True
    except Exception as e:
        logger.error(f"Error saving question and answer: {e}")
        session.rollback()
        return False
    finally:
        session.close()

# Create the tables if they don't exist
Base.metadata.create_all(engine)