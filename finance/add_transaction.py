import streamlit as st
import pandas as pd
from datetime import date
from db import connect_sql
from help_fun.time_taipei import t_today, t_now

def finance_add_transaction_page():
    st.title("➕ 新增交易紀錄")

    conn = connect_sql()
    df_cat = pd.read_sql("""
        SELECT id, name, parent_id
        FROM finance_category
        WHERE is_deleted = FALSE
        ORDER BY sort_order, id
    """, conn)

    df_acc = pd.read_sql("""
        SELECT id, name
        FROM finance_account
        ORDER BY id
    """, conn)
    conn.close()

    # --- 選擇交易類型 ---
    t_type = st.selectbox("交易類型", ["expense", "income", "transfer"])

    # --- 選擇帳戶 ---
    account_name = st.selectbox("主要帳戶", df_acc["name"].tolist())
    account_id = int(df_acc.loc[df_acc["name"] == account_name, "id"].iloc[0])
    amount = st.number_input("金額", min_value=0.0, step=100.0, format="%.2f")

    transfer_account_id = None
    if t_type == "transfer":
        transfer_name = st.selectbox("轉入帳戶", df_acc["name"].tolist())
        transfer_account_id = int(df_acc.loc[df_acc["name"] == transfer_name, "id"].iloc[0])

    # --- 選擇分類（僅收入/支出需要） ---
    category_id = None
    if t_type in ("expense", "income"):
        # 父分類
        parent_options = df_cat[df_cat["parent_id"].isna()]
        parent_choice = st.selectbox("父分類", ["(請選擇)"] + parent_options["name"].tolist())
        parent_id = None
        if parent_choice != "(請選擇)":
            parent_id = int(parent_options.loc[parent_options["name"] == parent_choice, "id"].iloc[0])

        # 子分類
        child_id = None
        if parent_id:
            child_options = df_cat[df_cat["parent_id"] == parent_id]
            child_choice = st.selectbox("子分類", ["(無)"] + child_options["name"].tolist())
            if child_choice != "(無)":
                child_id = int(child_options.loc[child_options["name"] == child_choice, "id"].iloc[0])

        # 孫分類
        grandchild_id = None
        if child_id:
            grandchild_options = df_cat[df_cat["parent_id"] == child_id]
            grandchild_choice = st.selectbox("孫分類", ["(無)"] + grandchild_options["name"].tolist())
            if grandchild_choice != "(無)":
                grandchild_id = int(grandchild_options.loc[grandchild_options["name"] == grandchild_choice, "id"].iloc[0])

        # 最終選中的分類
        category_id = grandchild_id or child_id or parent_id

    # --- 輸入其他欄位 ---
    t_date = st.date_input("日期", value=t_today())
    note = st.text_input("備註")

    # --- 提交 ---
    if st.button("✅ 新增交易"):
        if amount <= 0:
            st.error("❌ 金額必須大於 0")
        elif t_type in ("expense", "income") and category_id is None:
            st.error("❌ 收入/支出必須選擇分類")
        elif t_type == "transfer" and transfer_account_id is None:
            st.error("❌ 轉帳必須選擇轉入帳戶")
        elif t_type == "transfer" and transfer_account_id == account_id:
            st.error("❌ 轉帳帳戶不能相同")
        else:
            conn = connect_sql()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO finance_transaction 
                (category_id, account_id, transfer_account_id, amount, type, date, note)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (category_id, account_id, transfer_account_id, amount, t_type, t_date, note))
            conn.commit()
            conn.close()
            st.success(f"✅ 已新增 {t_type} 交易，金額 {amount:.2f}")
            st.rerun()