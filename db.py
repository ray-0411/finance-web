# import mysql.connector

import sqlite3

def get_connection():
    return sqlite3.connect("data.db", check_same_thread=False)