import streamlit as st
import pandas as pd
from datetime import date

from db import get_connection

def add_transaction_page():
    
    st.title("➕ 新增交易")
    
    
    # 載入下拉選單選項
    users_df = get_lookup("users", "id", "username")
    categories_df = get_lookup("categories", "id", "name")
    accounts_df = get_lookup("accounts", "id", "name")

    with st.form("add_transaction"):
        user_name = st.selectbox("👤 使用者", users_df["username"].tolist())
        user_id = users_df.loc[users_df["username"] == user_name, "id"].iloc[0]

        cat1_df = get_categories(1)
        category_name = st.selectbox("📂 分類1", cat1_df["name"].tolist())
        cat2_df = get_categories(2, category_name)
        category_name2 = st.selectbox("📂 分類2", cat2_df["name"].tolist())
        cat3_df = get_categories(3, category_name2)
        category_name3 = st.selectbox("📂 分類3", cat3_df["name"].tolist())
        
        account_name = st.selectbox("🏦 帳戶", accounts_df["name"].tolist())
        amount = st.number_input("💵 金額", min_value=0.0, step=100.0, format="%.2f")
        tx_type = st.selectbox("📌 類型", ["income", "expense"])
        date_value = st.date_input("📅 日期", date.today())
        note = st.text_area("📝 備註")

        submitted = st.form_submit_button("新增交易")
        
        if submitted:
            # 轉換成 ID
            user_id = users_df.loc[users_df["username"] == user_name, "id"].iloc[0]
            category_id = categories_df.loc[categories_df["name"] == category_name3, "id"].iloc[0]
            account_id = accounts_df.loc[accounts_df["name"] == account_name, "id"].iloc[0]

            insert_transaction(user_id, category_id, account_id, amount, tx_type, date_value, note)
            st.success("✅ 新交易已新增！")

# ========== 輔助函式 ==========
def get_lookup(table, id_col="id", name_col="name"):
    conn = get_connection()
    df = pd.read_sql(f"SELECT {id_col}, {name_col} FROM {table}", conn)
    conn.close()
    return df

def get_categories(level=1, parent_name=None):
    user_id = st.session_state.user_id
    conn = get_connection()
    sql = "SELECT id, name, parent_id FROM categories WHERE user_id = ? AND is_active = 1"
    df = pd.read_sql(sql, conn, params=(user_id,))
    conn.close()

    # 大分類：parent_id IS NULL
    if level == 1:
        return df[df["parent_id"].isnull()]

    # 次分類：parent_id = 上一層 id
    elif level == 2 and parent_name:
        parent_id = df.loc[df["name"] == parent_name, "id"].iloc[0]
        return df[df["parent_id"] == parent_id]

    # 細分類：parent_id = 上一層 id
    elif level == 3 and parent_name:
        parent_id = df.loc[df["name"] == parent_name, "id"].iloc[0]
        return df[df["parent_id"] == parent_id]

    else:
        return pd.DataFrame(columns=["id", "name", "parent_id"])


# ========== 新增交易 ==========
def insert_transaction(user_id, category_id, account_id, amount, tx_type, date_value, note):
    conn = get_connection()
    cursor = conn.cursor()
    sql = """
        INSERT INTO transactions (user_id, category_id, account_id, amount, type, date, note)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """

    # 🔹 強制轉型，避免 numpy.int64 / numpy.float64
    user_id = int(user_id)
    category_id = int(category_id)
    account_id = int(account_id)
    amount = float(amount)
    date_str = date_value.strftime("%Y-%m-%d")
    note = str(note or "")

    cursor.execute(sql, (user_id, category_id, account_id, amount, tx_type, date_str, note))
    conn.commit()
    conn.close()