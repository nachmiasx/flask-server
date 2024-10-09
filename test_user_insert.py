import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.users import Base, User, save_user, login_user
from db.question_answers import QuestionAnswer

# Replace with your actual database URL for testing
TEST_DB_HOST = os.getenv('DB_HOST')
TEST_DB_NAME = os.getenv('DB_NAME')
TEST_DB_USER = os.getenv('DB_USER')
TEST_DB_PASSWORD = os.getenv('DB_PASSWORD')
TEST_DB_PORT = os.getenv('DB_PORT')

TEST_DATABASE_URL = f"postgresql+psycopg2://{TEST_DB_USER}:{TEST_DB_PASSWORD}@{TEST_DB_HOST}:{TEST_DB_PORT}/{TEST_DB_NAME}"

# Set up the database engine and session factory
@pytest.fixture(scope='module')
def db_engine():
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(engine)  # Create tables in the test database
    yield engine
    Base.metadata.drop_all(engine)  # Drop tables after all tests are done

@pytest.fixture(scope='function')
def db_session(db_engine):
    """Creates a new database session for a test."""
    Session = sessionmaker(bind=db_engine)
    session = Session()
    yield session
    session.rollback()  # Roll back any changes after the test
    session.close()

def test_save_user(db_session):
    # Arrange
    email = "testuser@example.com"
    password = "SecurePassword123"

    # Act
    save_user(email, password)

    # Assert
    user = db_session.query(User).filter_by(email=email).first()

    assert user is not None, "User should be saved in the database."
    assert user.email == email, "Email should match the saved email."
    assert user.password_hash, "Password hash should not be empty."

def test_login_user(db_session):
    # Arrange
    email = "loginuser@example.com"
    password = "AnotherSecurePassword456"
    save_user(email, password)  # Save the user first

    # Act
    login_success = login_user(email, password)

    # Assert
    assert login_success, "User should be able to log in with correct credentials."

def test_failed_login(db_session):
    # Arrange
    email = "wronguser@example.com"
    password = "WrongPassword789"
    save_user("existinguser@example.com", "CorrectPassword")  # Save an existing user

    # Act
    login_success = login_user(email, password)

    # Assert
    assert not login_success, "User should not be able to log in with incorrect credentials."

