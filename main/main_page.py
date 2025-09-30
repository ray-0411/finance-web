import streamlit as st
import pandas as pd
from datetime import date, timedelta
from help_fun.time_taipei import t_today, t_now

from db import connect_sql

def main_page():
    start_date = t_today() - timedelta(days=7)
    end_date = t_today()

    conn = connect_sql()
    df = pd.read_sql("""
        SELECT
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
        GROUP BY root_name
    """, conn, params=(start_date, end_date))
    conn.close()

    st.markdown(
                f"""<div style='text-align:center;'>
                <h2>七日喝水分數</h2>
                </div>""",
                unsafe_allow_html=True
            )
    
    if df.empty:
        st.info("目前沒有任何飲用紀錄")
    else:
        water_score = float(df.loc[df["root_name"] == "water", "total_score"].sum())
        drink_score = float(df.loc[df["root_name"] == "drink", "total_score"].sum())

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(
                f"""<div style='text-align:center;'>
                <h2>💧 Water 總分數</h2>
                <h3>{water_score:.2f}</h3>
                </div>""",
                unsafe_allow_html=True
            )
        with col2:
            st.markdown(
                f"""<div style='text-align:center;'>
                <h2>🥤 Drink 總分數</h2>
                <h3>{drink_score:.2f}</h3>
                </div>""",
                unsafe_allow_html=True
            )
        st.markdown("---")