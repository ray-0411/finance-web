import sqlalchemy
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

DATABASE_WORK_URL = os.environ["DATABASE_WORK_URL"]

engine = sqlalchemy.create_engine(DATABASE_WORK_URL)

def connect_sql():
    return engine.raw_connection()