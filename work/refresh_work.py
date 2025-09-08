from datetime import date, timedelta

from db import connect_sql_work 

def generate_main_from_events(days_ahead=30):
    conn = connect_sql_work()
    cursor = conn.cursor()

    # 抓所有未刪除事件
    cursor.execute("SELECT id, date, repeat_type, repeat_value, expire FROM work_events WHERE stop = False")
    events = cursor.fetchall()

    today = date.today()
    end_date = today + timedelta(days=days_ahead)

    for event_id, start_date, repeat_type, repeat_value, expire in events:
        #start_date = date.fromisoformat(start_date)  # 轉換成 date

        if repeat_type == "none":
            if expire:
                if start_date <= end_date:
                    cursor.execute(
                        """
                        INSERT INTO work_main (event_id, occur_date)
                        VALUES (%s, %s)
                        ON CONFLICT (event_id, occur_date) DO NOTHING
                        """,
                        (event_id, start_date)
                    )
            else:
                if today <= start_date <= end_date:
                    cursor.execute(
                        """
                        INSERT INTO work_main (event_id, occur_date)
                        VALUES (%s, %s)
                        ON CONFLICT (event_id, occur_date) DO NOTHING
                        """,
                        (event_id, start_date)
                    )

        elif repeat_type == "day":
            # 隔幾天
            current = start_date
            while current <= end_date:
                if (current >= today) or expire:
                    cursor.execute(
                        """
                        INSERT INTO work_main (event_id, occur_date)
                        VALUES (%s, %s)
                        ON CONFLICT (event_id, occur_date) DO NOTHING
                        """,
                        (event_id, current)
                    )
                current += timedelta(days=repeat_value)

        elif repeat_type == "week":
            current = start_date
            while current <= end_date:
                if current >= today or expire:
                    cursor.execute(
                        """
                        INSERT INTO work_main (event_id, occur_date)
                        VALUES (%s, %s)
                        ON CONFLICT (event_id, occur_date) DO NOTHING
                        """,
                        (event_id, current)
                    )
                current += timedelta(weeks=repeat_value)

        elif repeat_type == "month":
            current = start_date
            anchor_day = start_date.day  # 錨定起始日的「日」
            while current <= end_date:
                if current >= today or expire:
                    cursor.execute(
                        """
                        INSERT INTO work_main (event_id, occur_date)
                        VALUES (%s, %s)
                        ON CONFLICT (event_id, occur_date) DO NOTHING
                        """,
                        (event_id, current)
                    )

                # 計算下一個日期（往後加 repeat_value 個月）
                month = current.month - 1 + repeat_value
                year = current.year + month // 12
                month = month % 12 + 1

                # 該月天數
                days_in_month = [31,
                    29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28,
                    31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1]

                # 嘗試用起始日的「日」，若該月沒有就補到月底
                day = anchor_day if anchor_day <= days_in_month else days_in_month

                current = date(year, month, day)


    conn.commit()
    conn.close()
    print("✅ 已依照 events 產生 main 表紀錄")

if __name__ == "__main__":
    generate_main_from_events(days_ahead=90)  # 產生未來 90 天
