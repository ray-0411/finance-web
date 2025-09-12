import streamlit as st
import pandas as pd
from datetime import date, datetime
import time
from db import connect_sql

def drink_add_page():
    st.title("🥤 新增飲用紀錄")

    # 抓所有分類
    conn = connect_sql()
    df_cat = pd.read_sql("""
        SELECT id, name, parent_id
        FROM drink_category
        WHERE is_deleted = FALSE
        ORDER BY id
    """, conn)
    conn.close()

    col1, col2 = st.columns(2)
    with col1:
        drink_date = st.date_input("日期", value=date.today())
    with col2:
        default_time = datetime.now().strftime("%H:%M")

        time_str = st.text_input("時間 (HH:MM)", value=default_time)
        if time_str:
            try:
                drink_time = datetime.strptime(time_str, "%H:%M").time()
            except ValueError:
                st.error("❌ 時間格式錯誤，請輸入 HH:MM")
                drink_time = None
        else:
            drink_time = None

    parent_options = df_cat[df_cat["parent_id"].isna()]
    parent_name = st.selectbox("type", parent_options["name"].tolist())

    parent_id = int(parent_options.loc[parent_options["name"] == parent_name, "id"].iloc[0])
    child_options = df_cat[df_cat["parent_id"] == parent_id]

    if not child_options.empty:
        if parent_id == 1:
            child_name = st.selectbox("大小", child_options["name"].tolist())
            child_id = int(child_options.loc[child_options["name"] == child_name, "id"].iloc[0])
        else:
            child_name = st.selectbox("飲料種類", child_options["name"].tolist())
            child_id = int(child_options.loc[child_options["name"] == child_name, "id"].iloc[0])
    else:
        child_id = parent_id
        child_name = None

    grandchild_options = df_cat[df_cat["parent_id"] == child_id]
    if not grandchild_options.empty:
        grandchild_name = st.selectbox("大小", grandchild_options["name"].tolist())
        category_id = int(grandchild_options.loc[grandchild_options["name"] == grandchild_name, "id"].iloc[0])
    else:
        category_id = child_id

    # --- 🔹 其他輸入 ---

    amount = st.number_input("數量", min_value=0, step=1, value=1)
    note = st.text_input("備註")

    # --- 🔹 新增按鈕 ---
    if st.button("✅ 新增紀錄"):
        conn = connect_sql()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO drink_main (drink_date, drink_time, amount, type, note, category_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (drink_date, drink_time, float(amount), "default", note, category_id))
        conn.commit()
        conn.close()

        st.success(f"已新增紀錄：{drink_date} {drink_time} - {amount} ml (分類ID={category_id})")
        time.sleep(0.5)
        st.rerun()
