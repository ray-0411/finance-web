import streamlit as st
import pandas as pd
from datetime import date, datetime
from zoneinfo import ZoneInfo
import time
from db import connect_sql
from help_fun.time_taipei import t_today, t_now

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
        default_date = t_now().date()
        
        drink_date = st.date_input("日期", value=default_date)
    with col2:
        default_time = t_now().strftime("%H:%M")

        time_str = st.text_input("時間 (HH:MM)", value=default_time)
        if time_str:
            try:
                drink_time = datetime.strptime(time_str, "%H:%M").time()
            except ValueError:
                st.error("❌ 時間格式錯誤，請輸入 HH:MM")
                drink_time = None
        else:
            drink_time = None

    def select_category(df_cat, max_depth=4):
        """
        df_cat: 資料表 (含 id, name, parent_id)
        max_depth: 最多展開幾層 (例如 4 表示 父→子→孫→曾孫)
        """
        current_id = None
        current_name = None

        # 第 0 層：root (parent_id 為空的)
        options = df_cat[df_cat["parent_id"].isna()]
        if options.empty:
            st.error("❌ 沒有任何分類")
            return None

        current_name = st.selectbox(f"第1層", options["name"].tolist())
        current_id = int(options.loc[options["name"] == current_name, "id"].iloc[0])

        # 往下找子層
        for depth in range(2, max_depth + 1):   # 從第2層開始
            sub_options = df_cat[df_cat["parent_id"] == current_id]
            if sub_options.empty:
                break
            sub_name = st.selectbox(f"第{depth}層", sub_options["name"].tolist())
            current_id = int(sub_options.loc[sub_options["name"] == sub_name, "id"].iloc[0])
            current_name = sub_name

        return current_id  # 最後選到的分類 id
    
    category_id = select_category(df_cat, max_depth=4)

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
        st.session_state["page"] = "drink_喝水紀錄"
        st.rerun()
