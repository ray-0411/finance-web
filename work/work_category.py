import streamlit as st
import pandas as pd
from db import connect_sql_work

def work_categories_page():
    st.title("📂 分類管理")

    # 1️⃣ 總表 (只顯示未刪除)
    conn = connect_sql_work()
    df = pd.read_sql("""
        SELECT c.id, c.name, p.name AS parent_name
        FROM category c
        LEFT JOIN category p ON c.parent_id = p.id
        WHERE c.is_deleted = FALSE
        ORDER BY c.id
    """, conn)
    conn.close()

    st.subheader("分類總表")
    st.dataframe(df, use_container_width=True)

    st.divider()

    # 2️⃣ 新增分類
    st.subheader("➕ 新增分類")
    with st.form("add_category_form", clear_on_submit=True):
        new_name = st.text_input("分類名稱")

        # 父分類（僅限未刪除的）
        parent_options = ["(無父分類)"] + df["name"].tolist()
        parent_name = st.selectbox("父分類", parent_options)
        parent_id = None if parent_name == "(無父分類)" else int(df.loc[df["name"] == parent_name, "id"].iloc[0])

        submitted = st.form_submit_button("新增")
        if submitted:
            if new_name.strip() == "":
                st.error("❌ 名稱不能為空")
            else:
                conn = connect_sql_work()
                cursor = conn.cursor()
                cursor.execute("INSERT INTO category (name, parent_id) VALUES (%s, %s)", (new_name, parent_id))
                conn.commit()
                conn.close()
                st.success(f"✅ 已新增分類：{new_name}")
                st.rerun()

    st.divider()

    # 3️⃣ 軟刪除分類
    st.subheader("🗑️ 刪除分類（軟刪除）")
    if len(df) > 0:
        delete_name = st.selectbox("選擇要刪除的分類", df["name"].tolist())
        delete_id = int(df.loc[df["name"] == delete_name, "id"].iloc[0])

        if st.button("刪除", type="primary"):
            conn = connect_sql_work()
            cursor = conn.cursor()
            # 軟刪除
            cursor.execute("UPDATE category SET is_deleted = TRUE WHERE id = %s", (delete_id,))
            conn.commit()
            conn.close()
            st.success(f"🗑️ 已軟刪除分類：{delete_name}")
            st.rerun()
    else:
        st.info("⚠️ 目前沒有分類可刪除")
