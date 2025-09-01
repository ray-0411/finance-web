# import mysql.connector

import sqlite3

def connect_sql_finance():
    return sqlite3.connect("finance.db", check_same_thread=False)