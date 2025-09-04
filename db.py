# import mysql.connector

import sqlite3

def connect_sql_finance():
    return sqlite3.connect("finance.db", check_same_thread=False)

# def connect_sql_work():
#     return sqlite3.connect("task.db", check_same_thread=False)

import sqlalchemy
import os

#DATABASE_URL = os.environ["DATABASE_URL"]

DATABASE_URL="postgresql://postgres:Ray0411ray@db.mcutdzuavjhjalkumynk.supabase.co:5432/postgres?sslmode=require&target_session_attrs=read-write"

engine = sqlalchemy.create_engine(DATABASE_URL)

def connect_sql_work():
    return engine.raw_connection()