# import mysql.connector

import sqlite3

def connect_sql_finance():
    return sqlite3.connect("finance.db", check_same_thread=False)

# def connect_sql_work():
#     return sqlite3.connect("task.db", check_same_thread=False)

import sqlalchemy
import os
from dotenv import load_dotenv
load_dotenv()

DATABASE_WORK_URL = os.environ["DATABASE_WORK_URL"]

engine = sqlalchemy.create_engine(DATABASE_WORK_URL)

def connect_sql_work():
    return engine.raw_connection()