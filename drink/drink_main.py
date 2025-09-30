import streamlit as st
import pandas as pd
from datetime import date, timedelta
from help_fun.time_taipei import t_today, t_now


from db import connect_sql

def drink_main_page():
    st.title("📋 我的飲用紀錄")
    
    # --- 🔹 日期區間選擇器 ---
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("開始日期", value=t_today()-timedelta(days=7))
    with col2:
        end_date = st.date_input("結束日期", value=t_today())

    if start_date > end_date:
        st.error("❌ 開始日期不能晚於結束日期")
        return

    conn = connect_sql()
    df = pd.read_sql("""
        SELECT m.id, m.drink_date, m.drink_time, m.amount, m.note,
            c.name AS category_name, 
            p.name AS parent_name, 
            gp.name AS grand_name,
            ggp.name AS great_name,
            
            COALESCE(ggp.name, gp.name, p.name, c.name) AS root_name,
            COALESCE(ggp.weight,1) * COALESCE(gp.weight,1) * COALESCE(p.weight,1) * COALESCE(c.weight,1) AS score
            
        FROM drink_main m
        LEFT JOIN drink_category c ON m.category_id = c.id
        LEFT JOIN drink_category p ON c.parent_id = p.id
        LEFT JOIN drink_category gp ON p.parent_id = gp.id
        LEFT JOIN drink_category ggp ON gp.parent_id = ggp.id
        WHERE m.drink_date BETWEEN %s AND %s
        ORDER BY m.drink_date DESC, m.drink_time DESC
    """, conn, params=(start_date, end_date))
    conn.close()

    if df.empty:
        st.info("目前沒有任何飲用紀錄")
        return

    # 組分類階層名稱
    def build_cat(row):
        parts = []
        if pd.notna(row["grand_name"]):
            parts.append(row["grand_name"])
        if pd.notna(row["parent_name"]):
            parts.append(row["parent_name"])
        if pd.notna(row["category_name"]):
            parts.append(row["category_name"])
        return " / ".join(parts)

    df["分類"] = df.apply(build_cat, axis=1)

    # 整理欄位顯示
    df_show = df[["drink_date", "drink_time", "amount", "score", "分類", "note", "root_name"]].copy()
    df_show.rename(columns={
        "drink_date": "日期",
        "drink_time": "時間",
        "amount": "數量",
        "score": "分數",
        "note": "備註",
        "root_name": "主分類"
    }, inplace=True)

    water_df = df_show[df_show["主分類"] == "water"].drop(columns=["主分類"])
    drink_df = df_show[df_show["主分類"] == "drink"].drop(columns=["主分類"])

    col1, col2 = st.columns(2)

    with col1:
        if not water_df.empty:
            water_score = (water_df['數量'] * water_df['分數']).sum()
            st.markdown(
                f"""<div style='text-align: center;'>
                <h2>💧 Water 總分數 </h2>
                <h3>{water_score:.2f}</h3>
                </div>""",
                unsafe_allow_html=True
            )
    with col2:
        if not drink_df.empty:
            st.markdown(
                f"""<div style='text-align: center;'>
                <h2>🥤 Drink 總分數 </h2>
                <h3>{(drink_df['數量'] * drink_df['分數']).sum():.2f}</h3>
                </div>""",
                unsafe_allow_html=True
            )
    st.markdown("---")

    if not water_df.empty:
        st.subheader("💧 Water 紀錄")
        st.dataframe(water_df, use_container_width=True)

    if not drink_df.empty:
        st.subheader("🥤 Drink 紀錄")
        st.dataframe(drink_df, use_container_width=True)
        
