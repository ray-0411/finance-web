import streamlit as st
import pandas as pd
import colorsys
from db import connect_sql
from streamlit_calendar import calendar

def drink_calendar_page():
    st.title("📅 月曆檢視（分數比例）")

    days = st.selectbox("計算範圍（包含當天往前幾天）", [7, 14, 28], index=0)

    conn = connect_sql()
    df = pd.read_sql("""
        SELECT m.id, m.drink_date, m.drink_time, m.amount, m.note,
                c.name AS category_name, p.name AS parent_name, gp.name AS grand_name,
                COALESCE(gp.name, p.name, c.name) AS root_name,
                COALESCE(gp.weight,1) * COALESCE(p.weight,1) * COALESCE(c.weight,1) AS score
        FROM drink_main m
        LEFT JOIN drink_category c ON m.category_id = c.id
        LEFT JOIN drink_category p ON c.parent_id = p.id
        LEFT JOIN drink_category gp ON p.parent_id = gp.id
        ORDER BY m.drink_date, m.drink_time
    """, conn)
    conn.close()

    if df.empty:
        st.info("目前沒有任何飲用紀錄")
        return

    # 每筆計算實際分數
    df["計分"] = df["amount"] * df["score"]

    # 每天 water / drink 分數
    df_day = df.groupby(["drink_date", "root_name"]).agg(total_score=("計分", "sum")).reset_index()
    df_pivot = df_day.pivot(index="drink_date", columns="root_name", values="total_score").fillna(0)
    df_pivot = df_pivot.rename(columns={"water": "water_score", "drink": "drink_score"}).reset_index()

    # 依日期排序
    df_pivot = df_pivot.sort_values("drink_date")
    
    # ⭐ 先補齊日期（包含沒有紀錄的日子）
    full_dates = pd.date_range(df_pivot["drink_date"].min(), df_pivot["drink_date"].max())
    df_pivot = df_pivot.set_index("drink_date").reindex(full_dates).reset_index()
    df_pivot = df_pivot.rename(columns={"index": "drink_date"})

    # ⭐ 沒紀錄的日子補 0（ratio 先不算）
    df_pivot[["water_score", "drink_score"]] = \
        df_pivot[["water_score", "drink_score"]].fillna(0)

    # rolling 計算「往前 N 天（包含當天）」的總和
    df_pivot["water_sum"] = df_pivot["water_score"].rolling(window=days, min_periods=1).sum()
    df_pivot["drink_sum"] = df_pivot["drink_score"].rolling(window=days, min_periods=1).sum()
    df_pivot["ratio"] = df_pivot.apply(
        lambda r: r["drink_sum"] / r["water_sum"] if r["water_sum"] > 0 else None,
        axis=1
    )
    
    



    # ===== 月曆顯示 =====
    st.subheader("🗓 互動月曆")

    def ratio_to_color(ratio):
        if pd.isna(ratio):
            return "#cccccc"  # 無數據 = 淺灰
        val = max(0.5, min(ratio, 1.5)) - 0.5  # 0.5~1.5 → 0~1

        # hue: 120 (綠) → 0 (紅)
        hue = (1 - val) * 120 / 360  # colorsys 用 0~1
        r, g, b = colorsys.hls_to_rgb(hue, 0.45, 1.0)  # H=色相, L=亮度, S=飽和度

        return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"


    events = []
    for _, row in df_pivot.iterrows():
        ratio_str = f"{row['ratio']:.2f}" if pd.notna(row['ratio']) else "—"
        color = ratio_to_color(row["ratio"])

        events.append({
            "title": f"📊{ratio_str}",
            "start": str(row["drink_date"]),
            "allDay": True,
            "color": color,
            "extendedProps": {                    # 額外資訊
                "water": f"{row['water_sum']:.1f}",
                "drink": f"{row['drink_sum']:.1f}"
            }
        })

    calendar_value = calendar(
        events=events,
        options={
            "initialView": "dayGridMonth",
            "locale": "zh-tw",
            "height": "auto",
            "firstDay": 1,
        },
        key="drink_calendar"
    )
    
    if calendar_value and calendar_value.get("callback") == "eventClick":
        e = calendar_value["eventClick"]["event"]
        props = e.get("extendedProps", {})

        water = props.get("water", "—")
        drink = props.get("drink", "—")
        ratio = e["title"].replace("📊", "")

        st.subheader(f"📅 {e['start']} 的紀錄")
        st.markdown(f"""
        - 💧 Water 分數：**{water}**
        - 🥤 Drink 分數：**{drink}**
        - 📊 比例：**{ratio}**
        """)

    st.markdown("---")

    st.subheader(f"📊 每 {days} 天累積分數")
    df_pivot = df_pivot.sort_values("drink_date", ascending=False)
    df_pivot = df_pivot[["drink_date", "ratio", "water_score", "drink_score", "water_sum", "drink_sum"]]
    st.dataframe(df_pivot, use_container_width=True)