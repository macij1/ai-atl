# main_page.py
import streamlit as st

# Function to switch pages using session state
def switch_page(page):
    st.session_state.active_page = page

# Initialize session state to track the active page
if 'active_page' not in st.session_state:
    st.session_state.active_page = 'main'

# Main landing page UI
st.markdown("<h1 style='text-align: center; margin-top: 50px;'>Welcome to I-Cite!</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; margin-bottom: 50px;'>How can we help you today?</h3>", unsafe_allow_html=True)


# Create a sidebar
with st.sidebar:
    st.title("AI ATL 2024 Hackathon")
    st.header("Authors")
    st.header("Many thanks to our hackathon sponsors:")
    st.write("- Streamlit")
    st.write("- Google Cloud")
    st.write("- Anthropic")
    st.markdown(
        "[![GitHub Repo](https://img.shields.io/badge/GitHub-Repo-181717?logo=github&style=for-the-badge)]"
        "(https://github.com/macij1/i-cite)"
    )


# Centered buttons with larger size and closer alignment
col1, col2, _ = st.columns([1, 1, 1], gap="small")
button_style = """
    <style>
        .stButton>button {
            width: 200px;
            height: 70px;
            font-size: 20px;
        }
    </style>
"""
st.markdown(button_style, unsafe_allow_html=True)

with col1:
    if st.button('🔍 Search', key='search_main'):
        switch_page('search')

with col2:
    if st.button('📄 Query', key='query_main'):
        switch_page('query')

# Navigate to the selected page
if st.session_state.active_page == 'search':
    from search_page import render_search_page
    render_search_page()
elif st.session_state.active_page == 'query':
    from query_page import render_query_page
    render_query_page()
