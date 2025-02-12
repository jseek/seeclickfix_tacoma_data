import streamlit as st

def stats(df):
    show_dataframe_stats(df)
    
def show_dataframe_stats(df):
    col_names = ", ".join(df.columns)
    st.write("Columns: ", col_names)