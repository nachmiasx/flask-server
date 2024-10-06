import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from logging.config import fileConfig
from alembic import context

load_dotenv()  # Load environment variables from .env file

# This is the Alembic Config object, which provides access
# to the values within the .ini file in use.
config = context.config

# Get values from environment variables
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_PORT = os.getenv('DB_PORT')

# Construct the database URL
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Set the sqlalchemy.url dynamically
config.set_main_option('sqlalchemy.url', DATABASE_URL)

# Interpret the config file for Python logging.
fileConfig(config.config_file_name)

# Enable SQL logging by setting echo=True in the engine (optional)
# You can also modify this to add echo only when in a debug mode.
engine = create_engine(DATABASE_URL, echo=True)  # Logs all SQL commands

# Import your metadata here if you're using SQLAlchemy models
# from myapp.models import Base
# target_metadata = Base.metadata

# This is needed to run migrations
target_metadata = None  # Set your target metadata if you're using models

def run_migrations_offline():
    """Run migrations in 'offline' mode.
    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well. By skipping the Engine creation
    we don't even need a DBAPI to be available.
    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.
    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    connectable = engine

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


# Choose the mode of execution for migrations
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
