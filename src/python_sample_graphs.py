class Paper:
    def __init__(self, doi, id:str=None, title:str=None, abstract:str=None, similarity:float=None, title_similarity:float=None, date:str=None, content:str=None) -> None:
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
    # Create sample Paper objects
    papers = [
        Paper(doi="10.1001/nlp.001", id="1", title="Neural Networks for NLP"),
        Paper(doi="10.1002/cv.002", id="2", title="Deep Learning in Computer Vision"),
        Paper(doi="10.1003/gan.003", id="3", title="Generative Adversarial Networks"),
        Paper(doi="10.1004/ml.004", id="4", title="Reinforcement Learning for Robotics"),
    ]

    # Create a list of citations (edges between papers)
    citations = [
        {'source_paper': papers[0].doi, 'cited_by': papers[1].doi},
        {'source_paper': papers[1].doi, 'cited_by': papers[2].doi},
        {'source_paper': papers[0].doi, 'cited_by': papers[3].doi},
        {'source_paper': papers[2].doi, 'cited_by': papers[3].doi}
    ]
    
    return papers, citations