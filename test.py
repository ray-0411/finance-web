from db import connect_sql_work


def work():
    with connect_sql_work() as conn:
        cur = conn.cursor()
        cur.execute("SELECT NOW()")
        print("✅ Connected to Supabase:", cur.fetchone())


if __name__ == "__main__":
    work()