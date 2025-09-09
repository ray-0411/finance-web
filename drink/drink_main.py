import streamlit as st
import pandas as pd
import datetime
from db import connect_sql  # 你原本的資料庫連線方法

def drink_main_page():
    st.title("💧 喝水 / 飲料紀錄")

    # 表單輸入
    with st.form("drink_form"):
        drink_date = st.date_input("日期", value=datetime.date.today())
        amount = st.number_input("數量", min_value=0.0, step=0.5)
        unit = st.text_input("單位", value="ml")
        drink_type = st.selectbox("種類", ["water", "drink"])
        note = st.text_input("備註")
        
        now = datetime.datetime.now()
        drink_time = now.time()

        submitted = st.form_submit_button("新增紀錄")
        if submitted:
            conn = connect_sql()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO other_drink (drink_date, drink_time, amount, unit, type, note)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (drink_date, drink_time, amount, unit, drink_type, note))
            conn.commit()
            conn.close()
            st.success("✅ 已新增紀錄！")

