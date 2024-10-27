# search_page.py
import streamlit as st
import json
from anthropic_client import AnthropicClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize session state for chat history
if 'messages' not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Welcome to I-Cite!"}]

# Initialize the Anthropic client
api_key = os.getenv("CLAUDE_API_KEY")
anthropic_client = AnthropicClient(api_key=api_key)

def render_search_page():
    """Render the Search Page UI."""
    st.title("📝 I-Cite")

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    question = st.chat_input("Ask something about the article:")

    if question:
        docs = "Ramanujam is the goat."
        msg = anthropic_client.get_response(docs, question)
        st.session_state.messages.append({"role": "user", "content": question})
        st.session_state.messages.append({"role": "assistant", "content": msg})
        st.chat_message("assistant").write(msg)
