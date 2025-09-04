from db import connect_sql_work


def work():
    conn = connect_sql_work()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO category (name, parent_id)
        VALUES (%s, %s)
    """, ("社團", None))
    conn.commit()

    # 在這裡執行你的資料庫操作

    conn.close()


if __name__ == "__main__":
    work()