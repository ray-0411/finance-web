# import mysql.connector

import sqlite3

def connect_sql_finance():
    return sqlite3.connect("finance.db", check_same_thread=False)

# def connect_sql_work():
#     return sqlite3.connect("task.db", check_same_thread=False)

import sqlalchemy
import os

DATABASE_WORK_URL = os.environ["DATABASE_WORK_URL"]

#DATABASE_WORK_URL="postgresql://postgres.mcutdzuavjhjalkumynk:Ray0411ray@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres?sslmode=require"



engine = sqlalchemy.create_engine(DATABASE_WORK_URL)

def connect_sql_work():
    return engine.raw_connection()