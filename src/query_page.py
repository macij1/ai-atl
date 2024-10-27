import streamlit as st
import asyncio
from database_endpoints import get_papers, get_related_papers
from query_arxiv import get_whole_documents
from anthropic_client import AnthropicClient
import os

async def fetch_papers_async(query):
    return await get_papers(query, 3)


async def call_claude_async(api_key, context_docs, query):
    claud_client = AnthropicClient(api_key=api_key)
    return await asyncio.to_thread(claud_client.get_response, context_docs, query)

def render_query_page():
    """Render the Query Page UI."""

    # Initialize session state variables
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'show_input' not in st.session_state:
        st.session_state.show_input = True
    if 'current_query' not in st.session_state:
        st.session_state.current_query = None
    if 'claude_response' not in st.session_state:
        st.session_state.claude_response = None

    # Set the title of the app
    st.markdown("<h1 style='text-align: center;'>Query Page</h1>", unsafe_allow_html=True)
    
    # Chat history display on the sidebar
    with st.sidebar:
        st.markdown("### Chat History 💭")
        for question in st.session_state.chat_history:
            st.text(question)

    # Check if input should be shown
    if st.session_state.show_input:
        query = st.chat_input("Type your question here...")

        # Check if a query has been submitted
        if query:
            # Update session state
            st.session_state.chat_history.append(query)
            st.session_state.current_query = query
            st.session_state.show_input = False  # Hide input after submission

            # Async function to handle fetching and processing
            async def handle_query():
                with st.spinner("Fetching papers..."):
                    six_papers = await get_papers(query)
                    st.session_state.papers, st.session_state.citations = await get_related_papers(query, six_papers)
                    ids = [paper.id for paper in six_papers]
                    dois = [paper.doi for paper in six_papers]
                    titles =  [paper.title for paper in six_papers]
                    context = ""
                with st.spinner("Fetching documents..."):
                    max_len = len(titles)
                    while max_len > 0:
                        try:
                            ids = ids[:max_len]
                            dois = dois[:max_len]
                            titles = titles[:max_len]
                            llm_context_docs = get_whole_documents(ids) # The good stuff (list)
                            for i in range(len(llm_context_docs)):
                                with open(llm_context_docs[i], "r") as f:
                                    doc=f.read()
                                context+="\nTITLE: "+str(titles[i]) + "\nDOI: "+str(dois[i]) +  "\nDOCUMENT\n "+str(doc)
                            break
                        except:
                            max_len -= 1

                with st.spinner("Calling Claude..."):
                    api_key = os.getenv("CLAUDE_API_KEY")
                    response = await call_claude_async(api_key, context, query)
                    st.session_state.claude_response = response  # Store response

                # Display Claude's response
                st.markdown("---")
                st.markdown("### Claude's Response")
                st.write(st.session_state.claude_response)  # Display the response

            # Run the async process
            asyncio.run(handle_query())

    # If user wants to ask another question, reset the input field
    if not st.session_state.show_input:
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("Ask Another Question", use_container_width=True):
                st.session_state.show_input = True  # Show input again
                st.session_state.current_query = None  # Reset current query
                st.session_state.claude_response = None  # Clear previous response

# Ensure to call your function if running as the main module
if __name__ == "__main__":
    render_query_page()
