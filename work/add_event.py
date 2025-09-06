import streamlit as st
import pandas as pd
from datetime import date
import time

from db import connect_sql_work 

def add_event_page():
    st.title("➕ 新增事件")

    with st.form("add_event_form"):
        title = st.text_input("事件標題")
        description = st.text_area("事件描述（選填）")
        event_date = st.date_input("開始日期", value=date.today())
        event_time = st.text_input("事件時間")

        # 分類選擇
        conn = connect_sql_work()
        df = pd.read_sql(f"SELECT id, name FROM category WHERE is_deleted = FALSE", conn)
        conn.close()
        category_name = st.selectbox("分類", df["name"].tolist())
        category_id = int(df.loc[df["name"] == category_name, "id"].iloc[0])

        repeat_type = st.selectbox("重複類型", ["none", "day", "week", "month"])
        repeat_value = st.number_input("重複值", min_value=1, step=1, value=1)

        priority = st.slider("重要度(5重要 1不重要)", 1, 5, 3)
        expire_val = st.checkbox("是否過期依舊提醒", value=False)

        submitted = st.form_submit_button("新增")
        if submitted:
            if title.strip() == "":
                st.error("❌ 標題不能為空")
            else:
                conn = connect_sql_work()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO events (title, description, date, time, category_id, repeat_type, repeat_value, priority, expire)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (title, description, event_date, event_time, category_id, repeat_type, repeat_value, priority, expire_val))
                conn.commit()
                conn.close()
                st.success(f"✅ 已新增事件：{title}")
                time.sleep(0.5)
                st.rerun()