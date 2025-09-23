from datetime import date, timedelta
from help_fun.time_taipei import t_today, t_now

from db import connect_sql

def generate_main_from_events(days_ahead=30):
    conn = connect_sql()
    cursor = conn.cursor()

    # 抓所有未刪除事件
    cursor.execute("""
                SELECT id, date, repeat_type, repeat_value, expire
                FROM work_events 
                WHERE stop = False
                """)
    events = cursor.fetchall()

    today = t_today()
    end_date = t_today() + timedelta(days=days_ahead)
    
    # 1️⃣ 先抓已有的 main (event_id, occur_date)
    cursor.execute("SELECT event_id, occur_date FROM work_main")
    existing = set(cursor.fetchall())   # {(event_id, occur_date), ...}
    

    # 2️⃣ 準備要新增的資料
    new_records = []

    for event_id, start_date, repeat_type, repeat_value, expire in events:

        def add_record(d):
            if (event_id, d) not in existing:
                new_records.append((event_id, d))

        if repeat_type == "none":
            if expire:
                if start_date <= end_date:
                    add_record(start_date)
            else:
                if today <= start_date <= end_date:
                    add_record(start_date)

        elif repeat_type == "day":
            current = start_date
            while current <= end_date:
                if (current >= today) or expire:
                    add_record(current)
                current += timedelta(days=repeat_value)

        elif repeat_type == "week":
            current = start_date
            while current <= end_date:
                if (current >= today) or expire:
                    add_record(current)
                current += timedelta(weeks=repeat_value)

        elif repeat_type == "month":
            current = start_date
            anchor_day = start_date.day
            while current <= end_date:
                if (current >= today) or expire:
                    add_record(current)

                month = current.month - 1 + repeat_value
                year = current.year + month // 12
                month = month % 12 + 1
                days_in_month = [
                    31,
                    29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28,
                    31, 30, 31, 30, 31, 31, 30, 31, 30, 31
                ][month - 1]
                day = anchor_day if anchor_day <= days_in_month else days_in_month
                current = date(year, month, day)

    # 3️⃣ 一次性批次 INSERT
    if new_records:
        cursor.executemany("""
            INSERT INTO work_main (event_id, occur_date)
            VALUES (%s, %s)
            ON CONFLICT (event_id, occur_date) DO NOTHING;
            """,
            new_records
        )

    conn.commit()
    conn.close()
    print(f"✅ 已新增 {len(new_records)} 筆資料")

