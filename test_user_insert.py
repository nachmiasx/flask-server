import unittest
# from your_user_management_file import save_user, login_user  # Import the functions from your main code
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.users import *  # Import your SQLAlchemy Base

# from db.users import User

# Replace with your actual database URL for testing
TEST_DB_HOST = os.getenv('DB_HOST')
TEST_DB_NAME = 'flask_db'  # Use a separate database for testing
TEST_DB_USER = os.getenv('DB_USER')
TEST_DB_PASSWORD = os.getenv('DB_PASSWORD')
TEST_DB_PORT = os.getenv('DB_PORT')

TEST_DATABASE_URL = f"postgresql+psycopg2://{TEST_DB_USER}:{TEST_DB_PASSWORD}@{TEST_DB_HOST}:{TEST_DB_PORT}/{TEST_DB_NAME}"

class TestUserManagement(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Set up the database connection for testing
        cls.engine = create_engine(TEST_DATABASE_URL)
        Base.metadata.create_all(cls.engine)  # Create tables in the test database

        cls.Session = sessionmaker(bind=cls.engine)

    @classmethod
    def tearDownClass(cls):
        # Drop the database tables after tests
        # Base.metadata.drop_all(cls.engine)
        return

    def test_save_user(self):
        # Arrange
        email = "testuser@example.com"
        password = "SecurePassword123"

        # Act
        save_user(email, password)

        # Assert
        session = self.Session()
        user = session.query(User).filter_by(email=email).first()
        session.close()

        self.assertIsNotNone(user, "User should be saved in the database.")
        self.assertEqual(user.email, email, "Email should match the saved email.")
        self.assertTrue(user.password_hash, "Password hash should not be empty.")

    def test_login_user(self):
        # Arrange
        email = "loginuser@example.com"
        password = "AnotherSecurePassword456"
        save_user(email, password)  # Save the user first

        # Act
        login_success = login_user(email, password)

        # Assert
        self.assertTrue(login_success, "User should be able to log in with correct credentials.")

    def test_failed_login(self):
        # Arrange
        email = "wronguser@example.com"
        password = "WrongPassword789"
        save_user("existinguser@example.com", "CorrectPassword")  # Save an existing user

        # Act
        login_success = login_user(email, password)

        # Assert
        self.assertFalse(login_success, "User should not be able to log in with incorrect credentials.")

if __name__ == "__main__":
    unittest.main()
