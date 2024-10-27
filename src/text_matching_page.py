import streamlit as st
import asyncio
from database_endpoints import fetch_substring_match
# from some_module import foo  # Import your function that retrieves papers

def render_text_matching_page():
    st.markdown("<h1 style='text-align: center;'>Text Matching</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Enter a substring to find matching papers</h3>", unsafe_allow_html=True)

    # Text input for the query
    query = st.text_input("Enter your query:", "")

    if st.button('Search'):
        if query:
            async def test():
                # Call the foo() function with the query
                results = await fetch_substring_match(query)  # Replace with your actual function to fetch papers

                if results:
                    st.markdown("<h3 style='text-align: center;'>Matching Papers</h3>", unsafe_allow_html=True)

                    # Display the results
                    for paper in results:
                        st.markdown(f"**Title:** {paper.title}")
                        st.markdown(f"**DOI:** {paper.doi}")
                        st.markdown(f"**Abstract:** {paper.abstract}")
                        st.markdown("---")  # Separator between papers
                else:
                    st.markdown("No matching papers found.")
            asyncio.run(test())
        else:
            st.warning("Please enter a query.")

# To render this page, the main_page.py will call `render_text_matching_page()`
