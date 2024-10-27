# graph_page.py
import streamlit as st

st.markdown("<h1 style='text-align: center; color: #FF7F50;'>Graph / Files Page</h1>", unsafe_allow_html=True)
st.write("This is where graphs or files will be displayed.")

if st.button("Back to Query"):
    st.session_state.active_page = 'query'
