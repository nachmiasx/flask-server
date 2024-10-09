import os
from sqlalchemy import engine_from_config, pool
from alembic import context
from logging.config import fileConfig
from dotenv import load_dotenv  # Make sure to import this to load .env variables
# from db.base import Base
# Import your models and metadata
from db.users import Base as UserBase, User
from db.question_answers import Base as QABase, QuestionAnswer

# Load environment variables from .env file
load_dotenv()
config = context.config

# Access the database credentials from environment variables
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')

# Construct the full database URL dynamically
SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Set the dynamically generated URL into the Alembic config
config.set_main_option('sqlalchemy.url', SQLALCHEMY_DATABASE_URL)

# This line sets up loggers basically.
fileConfig(config.config_file_name)

# Combine all metadata from your models
target_metadata = UserBase.metadata

# Other Alembic configurations (online/offline modes)
def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True, dialect_opts={"paramstyle": "named"}
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
