import streamlit as st
import pandas as pd
import time 
from db import connect_sql  

def drink_category_page():
    st.title("📂 分類管理")

    # 1️⃣ 讀取現有分類 (只顯示未刪除)
    conn = connect_sql()
    df = pd.read_sql("""
        SELECT id, name, parent_id, weight
        FROM drink_category
        WHERE is_deleted = FALSE
        ORDER BY id
    """, conn)
    conn.close()

    st.subheader("分類總表")
    st.dataframe(df, use_container_width=True)

    st.divider()

    # 2️⃣ 新增分類
    st.subheader("➕ 新增分類")
    with st.form("add_category_form", clear_on_submit=True):
        new_name = st.text_input("分類名稱")


        # 父分類
        conn = connect_sql()
        parent_df = pd.read_sql("""
            SELECT id, name, parent_id
            FROM drink_category
            WHERE is_deleted = FALSE
            AND (
                parent_id IS NULL               -- 頂層 (water, drink)
                OR parent_id = (
                    SELECT id FROM drink_category 
                    WHERE name = 'drink' AND parent_id IS NULL
                )
            )
            ORDER BY id
        """, conn)
        conn.close()

        parent_options = ["(無父分類)"] + [
            f"{row['name']}" for _, row in parent_df.iterrows()
        ]
        parent_name = st.selectbox("父分類", parent_options)

        # 權重
        weight = st.number_input("權重 (預設=1)", min_value=1, value=1)

        submitted = st.form_submit_button("新增分類")
        if submitted:
            conn = connect_sql()
            cursor = conn.cursor()

            # 找 parent_id
            parent_id = None
            if parent_name != "(無父分類)":
                parent_id = int(df[df["name"] == parent_name]["id"].iloc[0])

            cursor.execute("""
                INSERT INTO drink_category (name, parent_id, weight)
                VALUES (%s, %s, %s)
            """, (new_name, parent_id, weight))

            conn.commit()
            conn.close()
            st.success(f"✅ 已新增分類：{new_name}")
            time.sleep(0.5)
            st.rerun()

    st.divider()

    # 3️⃣ 刪除分類（雙層選擇）
    st.subheader("🗑 刪除分類")

    conn = connect_sql()
    all_df = pd.read_sql("""
        SELECT id, name, parent_id, is_deleted
        FROM drink_category
        WHERE is_deleted = FALSE
        ORDER BY id
    """, conn)

    # 找出 drink 的 id
    drink_id_df = pd.read_sql("""
        SELECT id
        FROM drink_category
        WHERE name = 'drink' AND parent_id IS NULL AND is_deleted = FALSE
        LIMIT 1
    """, conn)
    conn.close()
    drink_id = drink_id_df["id"].iloc[0] if not drink_id_df.empty else None

    if all_df.empty:
        st.info("目前沒有分類可以刪除")
    else:
        # 🔹 上層候選：NULL + 頂層 + drink 的子分類
        parent_candidates = []

        parent_candidates.append({"id": None, "name": "(NULL 上層)"})
        parent_candidates += all_df[all_df["parent_id"].isna()].to_dict("records")  # 頂層 water / drink
        if drink_id is not None:
            parent_candidates += all_df[all_df["parent_id"] == drink_id].to_dict("records")  # drink 的子分類

        parent_map = {r["id"]: r["name"] for r in parent_candidates}

        parent_id_sel = st.selectbox(
            "選擇上層分類",
            options=list(parent_map.keys()),
            format_func=lambda x: f"{parent_map[x]} (id={x})" if x is not None else parent_map[x]
        )

        # 🔹 子分類列表
        if parent_id_sel is None:
            children = all_df[all_df["parent_id"].isna()]  # 上層 NULL → 抓最上層
        else:
            children = all_df[all_df["parent_id"] == parent_id_sel]

        if children.empty:
            st.info("此上層目前沒有子分類")
        else:
            child_map = {int(r.id): r.name for _, r in children.iterrows()}
            child_id_sel = st.selectbox(
                "選擇要刪除的子分類",
                options=list(child_map.keys()),
                format_func=lambda x: f"{child_map[x]} (id={x})"
            )

            if st.button("刪除子分類", use_container_width=True):
                conn = connect_sql()
                cur = conn.cursor()
                cur.execute("UPDATE drink_category SET is_deleted = TRUE WHERE id = %s", (child_id_sel,))
                conn.commit()
                conn.close()
                st.success(f"✅ 已刪除子分類：{child_map[child_id_sel]}")
                st.rerun()