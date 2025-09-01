import streamlit as st
import pandas as pd
import time
from db import connect_sql_finance


def manage_categories_page():
    st.title("📂 分類管理")

    user_id = st.session_state.user_id
    if user_id is None:
        st.warning("⚠️ 請先選擇使用者")
        return


    # 大分類
    cat1_df = get_categories(None)
    cat1_name = st.selectbox("📂 大分類", ["None"] + cat1_df["name"].tolist())

    cat1_id = None
    if cat1_name != "None":
        cat1_id = int(cat1_df.loc[cat1_df["name"] == cat1_name, "id"].iloc[0])

    # 中分類
    cat2_df = get_categories(cat1_id) if cat1_id else pd.DataFrame()
    cat2_name = st.selectbox("📂 中分類", ["None"] + cat2_df["name"].tolist()) if not cat2_df.empty else "None"

    cat2_id = None
    if cat2_name != "None":
        cat2_id = int(cat2_df.loc[cat2_df["name"] == cat2_name, "id"].iloc[0])

    # 顯示子分類清單 + 決定 parent_id
    if cat1_id is None:
        st.subheader("大分類清單")
        st.dataframe(cat1_df)
        parent_id = None
    elif cat2_id is None:
        st.subheader(f"「{cat1_name}」的中分類清單")
        st.dataframe(cat2_df)
        parent_id = cat1_id
    else:
        cat3_df = get_categories(cat2_id)
        st.subheader(f"「{cat2_name}」的細分類清單")
        st.dataframe(cat3_df)
        parent_id = cat2_id

    # 新增區塊
    new_name = st.text_input("分類名稱")

    if st.button("新增分類"):
        if not new_name:
            st.error("❌ 請輸入分類名稱")
        else:
            insert_category(new_name, parent_id=parent_id)
            st.success(f"✅ 新增分類「{new_name}」成功！")
            st.rerun()

    # 刪除區塊
    df = get_categories(parent_id)
    
    if "delete_mode" not in st.session_state:
        st.session_state.delete_mode = False
        st.session_state.delete_target = None

    delete_name = st.selectbox("🗑️ 選擇要刪除的分類", ["None"] + df["name"].tolist())

    if not st.session_state.delete_mode:
        if delete_name != "None" and st.button(f"刪除「{delete_name}」"):
            st.session_state.delete_mode = True
            st.session_state.delete_target = delete_name
            st.rerun()
    else:
        st.warning(f"⚠️ 確定要刪除「{st.session_state.delete_target}」嗎？")
        if st.button("✅ 確定刪除"):
            cat_id = int(df.loc[df["name"] == st.session_state.delete_target, "id"].iloc[0])
            soft_delete_category(cat_id)
            st.success(f"✅ 已刪除「{st.session_state.delete_target}」及其子分類")
            st.session_state.delete_mode = False
            st.session_state.delete_target = None
            st.rerun()
        if st.button("❌ 取消"):
            st.session_state.delete_mode = False
            st.session_state.delete_target = None
            st.info("已取消刪除")
            time.sleep(0.5)
            st.rerun()
            


def get_categories(parent_id=None):
    conn = connect_sql_finance()
    if parent_id is not None:
        df = pd.read_sql(f"SELECT id, name FROM categories WHERE parent_id = {parent_id} AND is_active = 1", conn)
    else:
        df = pd.read_sql("SELECT id, name FROM categories WHERE parent_id IS NULL AND is_active = 1", conn)
    conn.close()
    return df


def insert_category(name, parent_id=None):
    conn = connect_sql_finance()
    cursor = conn.cursor()

    sql = """
        INSERT INTO categories (user_id, name, parent_id)
        VALUES (?, ?, ?)
    """
    cursor.execute(sql, (
        int(st.session_state.user_id),
        str(name),
        int(parent_id) if parent_id is not None else None
    ))
    
    conn.commit()
    conn.close()


def soft_delete_category(category_id, conn=None):
    close_conn = False
    if conn is None:
        conn = connect_sql_finance()
        close_conn = True
    cursor = conn.cursor()

    # 先停用自己
    cursor.execute("UPDATE categories SET is_active = 0 WHERE id = ?", (int(category_id),))

    # 找子分類
    cursor.execute("SELECT id FROM categories WHERE parent_id = ? AND is_active = 1", (int(category_id),))
    children = cursor.fetchall()

    # 遞迴停用子分類
    for (child_id,) in children:
        soft_delete_category(child_id, conn)

    
    if close_conn:
        conn.commit()
        conn.close()