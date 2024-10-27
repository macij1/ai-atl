# query_page.py
import streamlit as st

def render_query_page():
    """Render the Query Page UI."""
    def go_to_graph_page():
        st.session_state.active_page = 'graph'

    st.markdown("<h1 style='text-align: center; color: #34A853;'>Query Page</h1>", unsafe_allow_html=True)

    query_input = st.text_area("Write your query here")
    st.button("Run Query", key='run_query')

    if st.button("View Files"):
        go_to_graph_page()
