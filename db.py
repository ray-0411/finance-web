import sqlalchemy
import os
import pandas as pd

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

DATABASE_WORK_URL = os.environ["DATABASE_WORK_URL"]

engine = sqlalchemy.create_engine(DATABASE_WORK_URL)

def connect_sql():
    return engine.raw_connection()

def backup_all_tables():
    conn = connect_sql()
    cursor = conn.cursor()
    
    output_dir="db_backup"

    # 先查有哪些表
    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema='public'
        AND table_type='BASE TABLE'
    """)
    tables = [row[0] for row in cursor.fetchall()]

    print(f"📋 發現 {len(tables)} 張表：", tables)

    # 逐張表匯出
    for table in tables:
        df = pd.read_sql(f"SELECT * FROM {table}", conn)
        file_path = os.path.join(output_dir, f"{table}.csv")
        df.to_csv(file_path, index=False, encoding="utf-8-sig")
        print(f"✅ 匯出 {table} → {file_path}")

    conn.close()
    print("🎉 全部備份完成！")


if __name__ == "__main__":
    backup_all_tables()
