# filters/shelter_proximity_filter.py
import streamlit as st

def apply_shelter_proximity_filter():
    return st.toggle("Show only issues within 10 blocks of a shelter", value=False)
