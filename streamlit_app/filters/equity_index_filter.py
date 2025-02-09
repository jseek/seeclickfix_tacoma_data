# filters/equity_index_filter.py
import streamlit as st

def apply_equity_index_filter(df):
    options = ["All"] + sorted(df['equityindex'].dropna().unique().tolist())
    with st.expander("Filter by Equity Index", expanded=False):
        selected = st.selectbox("Select Equity Index", options)
    return selected
