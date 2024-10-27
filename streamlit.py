import streamlit as st
import anthropic

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
        h:1px;
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
    "- Streamlit"
    "- Google Cloud"
    "- Anthropic"
    "Check out our code!"
    st.markdown("[![GitHub Repo](https://img.shields.io/badge/GitHub-Repo-181717?logo=github&style=for-the-badge)](https://github.com/macij1/i-cite)")

# Main title and header
st.title("📝 I-Cite")

# Specify the file path and read content
file_path = 'aiayn.txt'  # Update to your file path
try:
    with open(file_path, 'r', encoding='utf-8') as file:
        docs = file.read()
except FileNotFoundError:
    st.error("File not found. Please check the path.")
    docs = ''

# Initialize the Anthropic client
client = anthropic.Client(api_key="your_api_key_here")  # Replace with your actual API key

# Display chat history
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# User input for the question
question = st.chat_input("Ask something about the article:")

# Process the input when a question is provided
if question:
    # Prepare the prompt for the model
    prompt = f"{anthropic.HUMAN_PROMPT} Here's the article:\n\n{docs}\n\nQuestion: {question}{anthropic.AI_PROMPT}"

    # Send the prompt to the model
    response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=100,
        messages=[{"role": "user", "content": prompt}]
    )

    # Extract the content text safely
    text_block = response['content'][0]
    msg = text_block.split("text='")[1].split("'")[0]

    # Add the user's question and assistant's response to the session state
    st.session_state.messages.append({"role": "user", "content": question})
    st.session_state.messages.append({"role": "assistant", "content": msg})

    # Display the assistant's response
    st.chat_message("assistant").write(msg)
