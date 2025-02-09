import streamlit as st

def issue_data_table(df):
    st.subheader("Issue Data Table")
    st.markdown("Details on each issue.")
    st.dataframe(df)