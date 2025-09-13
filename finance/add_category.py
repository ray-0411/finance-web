import streamlit as st
import pandas as pd
from db import connect_sql

def finance_add_category_page(category_id=0):
    
    mode = "新增" if category_id == 0 else "編輯"
    st.title(f"📂 {mode}財務分類 (三層)")

    conn = connect_sql()
    df_cat = pd.read_sql("""
        SELECT id, name, parent_id, type
        FROM finance_category 
        WHERE is_deleted = FALSE
        ORDER BY sort_order, id
    """, conn)

    df_acc = pd.read_sql("""
        SELECT id, name 
        FROM finance_account
        ORDER BY id
    """, conn)

    # 如果是編輯模式，載入資料
    if category_id != 0:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, parent_id, default_account_id, sort_order, type
            FROM finance_category
            WHERE id = %s
        """, (category_id,))
        row = cursor.fetchone()
        cursor.close()
        if not row:
            st.error("❌ 找不到該分類")
            conn.close()
            return
        (cid, name, parent_id, default_account_id, sort_order, type) = row
    else:
        # 新增模式 → 預設值
        cid = 0
        name = ""
        parent_id = None
        default_account_id = None
        sort_order = 0
        type = "expense"  # 預設新增的分類為支出

    conn.close()

    # --- 輸入元件 ---
    name = st.text_input("分類名稱", value=name)

    # 🔹 父分類 (第一層)
    parent_options_df = df_cat[df_cat["parent_id"].isna()]
    parent_options = ["(無父分類)"] + parent_options_df["name"].tolist()
    parent_default_index = 0
    if parent_id and parent_id in parent_options_df["id"].values:
        parent_default_index = parent_options_df.index[parent_options_df["id"] == parent_id].tolist()[0] + 1
    parent_choice = st.selectbox("父分類", parent_options, index=parent_default_index)
    chosen_parent_id = None
    if parent_choice != "(無父分類)":
        chosen_parent_id = int(parent_options_df.loc[parent_options_df["name"] == parent_choice, "id"].iloc[0])

    # 🔹 子分類 (第二層)
    child_id = None
    child_default_index = 0
    if chosen_parent_id:
        child_options_df = df_cat[df_cat["parent_id"] == chosen_parent_id]
        child_options = ["(無子分類)"] + child_options_df["name"].tolist()
        if parent_id and parent_id in child_options_df["id"].values:
            child_default_index = child_options_df.index[child_options_df["id"] == parent_id].tolist()[0] + 1
        child_choice = st.selectbox("子分類", child_options, index=child_default_index)
        if child_choice != "(無子分類)":
            child_id = int(child_options_df.loc[child_options_df["name"] == child_choice, "id"].iloc[0])

    
    # ➡️ 最後 parent_id
    final_parent_id = child_id or chosen_parent_id

    # 🔹 預設帳戶
    acc_options = ["(無預設帳戶)"] + df_acc["name"].tolist()
    acc_default_index = 0
    if default_account_id and default_account_id in df_acc["id"].values:
        acc_default_index = df_acc.index[df_acc["id"] == default_account_id].tolist()[0] + 1
    acc_choice = st.selectbox("預設帳戶", acc_options, index=acc_default_index)
    if acc_choice != "(無預設帳戶)":
        default_account_id = int(df_acc.loc[df_acc["name"] == acc_choice, "id"].iloc[0])
    else:
        default_account_id = None

    if chosen_parent_id is None:
        cat_type = st.selectbox(
            "分類類型",
            ["income", "expense", "both"],
            index=["income", "expense", "both"].index(
                (type if category_id != 0 else "expense")  # 編輯時帶入原值，新增時預設 expense
            )
        )
    else:
        # parent_id 不為 None，表示是子分類
        # 用parent的type來決定
        parent_type = df_cat.loc[df_cat["id"] == chosen_parent_id, "type"].iloc[0]
        cat_type = parent_type
        st.info(f"ℹ️ 由於有父分類，類型自動設定為：{cat_type}")

    sort_order = st.number_input("排序", min_value=0, step=1, value=sort_order)

    # --- 提交 ---
    if st.button("✅ " + ("新增" if cid == 0 else "更新")):
        if name.strip() == "":
            st.error("❌ 分類名稱不能為空")
        else:
            conn = connect_sql()
            cursor = conn.cursor()
            if cid == 0:
                cursor.execute("""
                    INSERT INTO finance_category (name, parent_id, default_account_id, sort_order, type)
                    VALUES (%s, %s, %s, %s, %s)
                """, (name, final_parent_id, default_account_id, sort_order, cat_type))
                st.success(f"✅ 已新增分類：{name}")
            else:
                cursor.execute("""
                    UPDATE finance_category
                    SET name = %s, parent_id = %s, default_account_id = %s, sort_order = %s, type = %s
                    WHERE id = %s
                """, (name, final_parent_id, default_account_id, sort_order, cat_type, cid))
                st.success(f"✅ 已更新分類：{name}")
            conn.commit()
            conn.close()
            st.rerun()
