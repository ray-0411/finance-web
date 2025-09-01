import streamlit as st
import pandas as pd
from db import connect_sql_finance


def get_transaction_page():
    st.subheader("📊 最近 50 筆交易")
    df = get_transactions()
    st.dataframe(df)

# ========== 讀取交易 ==========
def get_transactions():
    conn = connect_sql_finance()
    df = pd.read_sql("""
        SELECT t.id, u.username AS user, c.name AS category, a.name AS account,
            t.amount, t.type, t.date, t.note, t.created_at
        FROM transactions t
        JOIN users u ON t.user_id = u.id
        JOIN categories c ON t.category_id = c.id
        JOIN accounts a ON t.account_id = a.id
        ORDER BY t.id DESC LIMIT 50
    """, conn)
    conn.close()
    return df
