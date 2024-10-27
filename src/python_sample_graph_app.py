import streamlit as st
import networkx as nx
from pyvis.network import Network
import tempfile
from pathlib import Path
import streamlit.components.v1 as components
from datetime import datetime

class Paper:
    def __init__(self, doi, id:str=None, title:str=None, abstract:str=None, 
                 similarity:float=None, title_similarity:float=None, 
                 date:str=None, content:str=None) -> None:
        self.id: str = id
        self.doi: str = doi
        self.title: str = title
        self.abstract: str = abstract
        self.similarity: float = similarity
        self.title_similarity: float = title_similarity
        self.date = date
        self.content: str = content

    def __str__(self) -> str:
        return f"doi: {self.doi}"

    def __repr__(self):
        return f"doi: {self.doi}, id: {self.id}, title: {self.title}\n"

def load_sample_data():
    papers = [
        Paper(doi="10.1001/nlp.001", id="1", title="Neural Networks for NLP",
              abstract="This paper explores the application of neural networks in natural language processing tasks.",
              similarity=0.85, date="2022-01-15"),
        Paper(doi="10.1002/cv.002", id="2", title="Deep Learning in Computer Vision",
              abstract="A comprehensive study of deep learning methods in computer vision applications.",
              similarity=0.75, date="2022-03-20"),
        Paper(doi="10.1003/gan.003", id="3", title="Generative Adversarial Networks",
              abstract="Introduction to GANs and their applications in image generation.",
              similarity=0.65, date="2022-06-10"),
        Paper(doi="10.1004/ml.004", id="4", title="Reinforcement Learning for Robotics",
              abstract="Exploring the use of reinforcement learning in robotic control systems.",
              similarity=0.70, date="2022-09-05")
    ]
    
    citations = [
        {'source_paper': papers[0].doi, 'cited_by': papers[1].doi},
        {'source_paper': papers[1].doi, 'cited_by': papers[2].doi},
        {'source_paper': papers[0].doi, 'cited_by': papers[3].doi},
        {'source_paper': papers[2].doi, 'cited_by': papers[3].doi}
    ]
    return papers, citations

def create_network_html(papers, citations, selected_paper=None, date_range=None, min_similarity=0.0):
    """Create an interactive network visualization with enhanced features."""
    G = nx.DiGraph()
    
    # Color scheme
    colors = ['#4285F4', '#EA4335', '#FBBC05', '#34A853', '#7B1FA2', '#1976D2']
    paper_colors = {paper.doi: colors[i % len(colors)] for i, paper in enumerate(papers)}
    
    # Process papers and add nodes
    for paper in papers:
        # Skip if paper doesn't meet similarity threshold
        if paper.similarity and paper.similarity < min_similarity:
            continue
            
        # Skip if paper is outside date range
        if date_range and paper.date:
            paper_date = datetime.strptime(paper.date, '%Y-%m-%d').date()
            if paper_date < date_range[0] or paper_date > date_range[1]:
                continue
        
        # Calculate node size based on similarity
        size = 30 if not paper.similarity else 20 + (paper.similarity * 30)
        
        # Determine if node should be highlighted
        border_width = 3 if selected_paper and paper.doi == selected_paper.doi else 1
        
        G.add_node(
            paper.doi,
            title=f"""
                <div style='max-width:300px'>
                    <h3>{paper.title}</h3>
                    <p><b>DOI:</b> {paper.doi}</p>
                    <p><b>Date:</b> {paper.date}</p>
                    <p><b>Similarity:</b> {f"{paper.similarity:.2f}" if paper.similarity else "N/A"}</p>
                    <p><b>Abstract:</b> {paper.abstract}</p>
                </div>
            """,
            size=size,
            color=paper_colors[paper.doi],
            borderWidth=border_width,
            label=paper.title[:30] + "..." if len(paper.title) > 30 else paper.title
        )
    
    # Add edges
    for citation in citations:
        if citation['source_paper'] in G.nodes and citation['cited_by'] in G.nodes:
            G.add_edge(citation['cited_by'], citation['source_paper'])
    
    # Create Pyvis network
    net = Network(height="600px", width="100%", bgcolor="#ffffff", font_color="black", directed=True)
    
    # Configure physics for better visualization
    net.force_atlas_2based(
        gravity=-100,
        central_gravity=0.01,
        spring_length=200,
        spring_strength=0.05,
        damping=0.4,
        overlap=0
    )
    
    # Add nodes and edges
    net.from_nx(G)
    
    # Customize edges
    for edge in net.edges:
        edge['arrows'] = 'to'
        edge['color'] = '#666666'
        edge['width'] = 2
        edge['smooth'] = {'type': 'curvedCW', 'roundness': 0.2}
    
    # Save and return path
    with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as tmp:
        net.save_graph(tmp.name)
        return tmp.name

def calculate_network_stats(papers, citations):
    cited_counts = {}
    citing_counts = {}

    for citation in citations:
        cited_counts[citation['source_paper']] = cited_counts.get(citation['source_paper'], 0) + 1
        citing_counts[citation['cited_by']] = citing_counts.get(citation['cited_by'], 0) + 1

    most_cited = max(cited_counts.items(), key=lambda x: x[1], default=('None', 0))
    most_citing = max(citing_counts.items(), key=lambda x: x[1], default=('None', 0))

    most_cited_paper = next((p.title for p in papers if p.doi == most_cited[0]), 'None')
    most_citing_paper = next((p.title for p in papers if p.doi == most_citing[0]), 'None')

    # Use tooltips to show full paper names
    stats = {
        'Papers': len(papers),
        'Citations': len(citations),
        'Most Cited Paper': f"<span title='{most_cited_paper}'>{most_cited_paper[:30]}...</span>" if len(most_cited_paper) > 30 else most_cited_paper,
        'Most Citations Made': f"<span title='{most_citing_paper}'>{most_citing_paper[:30]}...</span>" if len(most_citing_paper) > 30 else most_citing_paper,
    }

    return stats

def main():
    st.set_page_config(layout="wide", page_title="Citation Network")
    
    # Load data
    papers, citations = load_sample_data()
    
    # Sidebar with paper list and controls
    st.sidebar.header("Papers")
    
    # Paper links with icons and better formatting
    for paper in papers:
        st.sidebar.markdown(f"""
        <div style='background-color: #f0f2f6; padding: 10px; border-radius: 5px; margin-bottom: 10px; color: #333;'>
            <b>{paper.title}</b><br>
            📄 <a href='https://doi.org/{paper.doi.replace("doi:", "")}' target='_blank'>{paper.doi}</a>
        </div>
        """, unsafe_allow_html=True)
    
    # Paper selection for highlighting
    selected_paper = st.sidebar.selectbox(
        "Highlight Paper",
        [None] + papers,
        format_func=lambda x: x.title if x else "None"
    )
    
    # Similarity threshold with better formatting
    min_similarity = st.sidebar.slider(
        "Minimum Similarity Score",
        min_value=0.0,
        max_value=1.0,
        value=0.0,
        step=0.1,
        format="%0.1f"
    )
    
    # Date range with better formatting
    if any(p.date for p in papers):
        dates = [datetime.strptime(p.date, '%Y-%m-%d').date() for p in papers if p.date]
        min_date, max_date = min(dates), max(dates)
        date_range = st.sidebar.date_input(
            "Filter by Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        if isinstance(date_range, tuple) and date_range[0] and date_range[1]:
            date_range = (date_range[0], date_range[1])
        else:
            date_range = None
    else:
        date_range = None
    
    # Main content area
    col1, col2 = st.columns([7, 3])
    
    with col1:
        st.title("Paper Citation Network")
        
        # Create and display network
        html_path = create_network_html(papers, citations, selected_paper, date_range, min_similarity)
        with open(html_path, 'r', encoding='utf-8') as f:
            components.html(f.read(), height=600)
        Path(html_path).unlink()
        
        # Paper details card with better styling
        if selected_paper:
            st.markdown(f"""
            <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; color: #333;'>
                <h3 style='color: black;'>{selected_paper.title}</h3>
                <p><b>DOI:</b> <a href='https://doi.org/{selected_paper.doi.replace("doi:", "")}' target='_blank'>{selected_paper.doi}</a></p>
                <p><b>Date:</b> {selected_paper.date}</p>
                <p><b>Similarity Score:</b> {f"{selected_paper.similarity:.2f}" if selected_paper.similarity else "N/A"}</p>
                <p><b>Abstract:</b></p>
                <p>{selected_paper.abstract if selected_paper.abstract else 'No abstract available'}</p>
            </div>
            """, unsafe_allow_html=True)
    

    with col2:
        st.header("Interactive Features")
        st.markdown("""
        - 🔍 **Zoom:** Use mouse wheel or pinch gesture
        - 🖱️ **Pan:** Click and drag on empty space
        - ✨ **Move Nodes:** Click and drag nodes
        - 📝 **View Details:** Hover over nodes for paper information
        - 🎯 **Highlight:** Select a paper from sidebar to highlight
        - 📊 **Filter:** Use similarity slider and date range
        - 🔗 **Links:** Click DOIs to view papers
        """)

        st.header("Network Statistics")
        stats = calculate_network_stats(papers, citations)
        cols = st.columns(2)
        for i, (stat, value) in enumerate(stats.items()):
            cols[i % 2].markdown(f"<b>{stat}:</b> {value}", unsafe_allow_html=True)

    
    # Interactive features guide


if __name__ == "__main__":
    main()