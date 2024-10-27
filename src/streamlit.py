import streamlit as st
import json
from anthropic_client import AnthropicClient  # New import
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize session state for chat history if it doesn't exist
if 'messages' not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Welcome to I-Cite!"}]

# Add custom CSS to position the SVG
st.markdown(
    """
    <style>
    .fixed-svg {
        position: fixed;
        top: 10px;
        right: 10px;
        z-index: 10;
        height: 1px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Sidebar with GitHub link
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

# Main title and header
st.title("📝 I-Cite")

# Initialize the Anthropic client
api_key = os.getenv("CLAUDE_API_KEY")
anthropic_client = AnthropicClient(api_key=api_key)

# Display chat history
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# User input for the question
question = st.chat_input("Ask something about the article:")

if question:

    docs = "Ramanujam is the goat."
    # Get response from Anthropic API
    msg = anthropic_client.get_response(docs, question)

    # Add the user's question and assistant's response to the session state
    st.session_state.messages.append({"role": "user", "content": question})
    st.session_state.messages.append({"role": "assistant", "content": msg})

    # Display the assistant's response
    st.chat_message("assistant").write(msg)
