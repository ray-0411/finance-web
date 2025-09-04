import sqlite3

from db import connect_sql_work

DB_PATH = "task.db"  # 你要存的資料庫檔名

def work():
    conn = connect_sql_work()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO category (name, parent_id)
        VALUES (?, ?)
    """, ("家庭", None))
    conn.commit()

    # 在這裡執行你的資料庫操作

    conn.close()


if __name__ == "__main__":
    work()