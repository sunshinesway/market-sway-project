# connection helper to read database from env and return connection
# prevent duplicate connection logic
#
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

from dotenv import load_dotenv
import os

def get_db_values():
    load_dotenv()
    db_user = os.getenv('POSTGRES_USER')
    db_pw = os.getenv('POSTGRES_PASSWORD')
    db_name = os.getenv('POSTGRES_DB')
    host_name = os.getenv('POSTGRES_HOST', 'localhost')
    port_value = os.getenv('POSTGRES_PORT', '5433')
    
    return db_user, db_pw, db_name, host_name, port_value

def get_engine():
    
    db_user, db_pw, db_name, host_name, port_value = get_db_values()
    # "postgresql+psycopg2://<user>:<password>@<host>:<port>/<database>"
    # <user>: PostgreSQL username (e.g., myuser).
    # <password>: User password (e.g., mypassword).
    # <host>: The address of the PostgreSQL server. For Docker, this depends on where your Python script is running (see Fix 3).
    # <port>: The host port mapped to the container (default: 5432).
    # <database>: Database name (e.g., mydb).
    #
    DATABASE_URL = f'postgresql+psycopg2://{db_user}:{db_pw}@{host_name}:{port_value}/{db_name}'
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    try: # quick connectivity test
       with engine.connect() as conn:
        print("Successfully connected to PostgreSQL!")
    except OperationalError as e:
        print(f"Connection failed: {e}")
        raise

    return engine