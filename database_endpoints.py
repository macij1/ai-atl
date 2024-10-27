from pgvector.asyncpg import register_vector
import asyncio
import asyncpg
from google.cloud.sql.connector import Connector
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel
import os
from typing import Union

tokenizer = AutoTokenizer.from_pretrained('jinaai/jina-embeddings-v3')
model = AutoModel.from_pretrained('jinaai/jina-embeddings-v3', trust_remote_code=True)

project_id = os.getenv("PROJECT_ID")
database_password = os.getenv('DATABASE_PASSWORD')
region = "us-central1"
instance_name = "research-paper-db"
database_name = "research-papers"
database_user = os.getenv("DATABASE_USER")

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

async def test_connection():
    """
    Tests the connection to a Cloud SQL database using the asyncpg driver.

    This asynchronous function establishes a connection to the specified Cloud SQL instance
    and retrieves the database version as a simple connectivity check. 

    Raises:
        Any exceptions raised by the Connector or asyncpg during the connection process 
        or while executing the SQL query will propagate up to the caller.

    Example:
        await test_connection()
    """
    loop = asyncio.get_running_loop()
    # initialize Connector object as async context manager
    async with Connector(loop=loop) as connector:
        # create connection to Cloud SQL database
        conn: asyncpg.Connection = await connector.connect_async(
            f"{project_id}:{region}:{instance_name}",  # Cloud SQL instance connection name
            "asyncpg",
            user=f"{database_user}",
            password=f"{database_password}",
            db=f"{database_name}"
            # ... additional database driver args
        )

        # query Cloud SQL database
        results = await conn.fetch("SELECT version()")
        print(results[0]["version"])

        # close asyncpg connection
        await conn.close()

async def _fetch_similarity(embeding: np.ndarray, nbr_articles=3, DESC=True) -> list[Paper]:
    """
    Fetch similar articles from the database based on a given embedding vector.

    This method connects to a Cloud SQL database and retrieves a specified number
    of articles that are most similar to the provided embedding. Similarity is 
    calculated using cosine similarity over the vector embeddings stored in the 
    'papers' table. 

    Parameters:
    - embedding (np.ndarray): The embedding vector representing the query article.
    - nbr_articles (int, optional): The number of similar articles to retrieve. Default is 2.
    - DESC (bool, optional): Whether to sort the results in descending order of similarity. 
                             Default is True.

    Returns:
    - List[dict]: A list of dictionaries, each containing the following keys:
        - "doi": Digital Object Identifier for the article.
        - "id": Identifier for the article.
        - "title": Title of the similar article.
        - "abstract": Abstract of the similar article.
        - "similarity": Cosine similarity score of the article.
        - "title_similarity": Similarity score based on title embeddings.

    Raises:
    - Exception: If no results are found, an exception is raised indicating to adjust 
                 the query parameters.

    Note:
    Ensure that the pgvector extension is registered for proper handling of vector 
    embeddings.
    """
    loop = asyncio.get_running_loop()
    async with Connector(loop=loop) as connector:
        # Create connection to Cloud SQL database.
        conn: asyncpg.Connection = await connector.connect_async(
            f"{project_id}:{region}:{instance_name}",  # Cloud SQL instance connection name
            "asyncpg",
            user=f"{database_user}",
            password=f"{database_password}",
            db=f"{database_name}",
        )

        await register_vector(conn)
        # Find similar products to the query using cosine similarity search
        # over all vector embeddings. This new feature is provided by `pgvector`.
        results1 = await conn.fetch(
            f"""
            SELECT doi, id, title, 1 - (embedding <=> $1) AS similarity, abstract, 1 - (title_embedding <=> $1) AS title_similarity 
            FROM papers
            ORDER BY similarity {"DESC" if DESC else ""}
            LIMIT $2
            """,
            embeding,
            nbr_articles
        )

        results2 = await conn.fetch(
            f"""

            SELECT doi, id, title, 1 - (embedding <=> $1) AS similarity, abstract, 
                1 - (title_embedding <=> $1) AS title_similarity
            FROM papers
            WHERE doi NOT IN (
                SELECT doi
                FROM papers
                ORDER BY 1 - (embedding <=> $1) {"DESC" if DESC else ""}
                LIMIT $2
            )
            ORDER BY similarity {"DESC" if DESC else ""}
            LIMIT $2;

            """,
            embeding,
            nbr_articles
        )

        if len(results1) + len(results2) == 0:
            raise Exception("Did not find any results. Adjust the query parameters.")
        matches = []
        for r in results1 + results2:
            # Collect the description for all the matched similar toy products.
            matches.append(Paper(*r))

        await conn.close()
        return matches
    
async def _fetch_similarity_from_list(embedding: np.ndarray, bois: list[str], DESC=True) -> list[Paper]:
    """
    Fetches similar papers from the database based on the provided embedding and a list of DOIs.

    This method establishes a connection to a Cloud SQL database and retrieves a list of papers
    whose DOIs match those in the provided list. The similarity is calculated using cosine similarity
    based on the given embedding. The results are sorted by similarity in descending order (or ascending
    if specified) and limited to the number of articles specified.

    Args:
        embedding (np.ndarray): The embedding vector used to compute similarity.
        bois (list[str]): A list of DOIs to filter the papers by.
        nbr_articles (int, optional): The maximum number of articles to return. Defaults to 3.
        DESC (bool, optional): If True, sorts the results in descending order of similarity. Defaults to True.

    Returns:
        list[Paper]: A list of `Paper` objects representing the similar papers found in the database.

    Raises:
        Exception: Raises an exception if no results are found.
    """
    if not bois: return []
    loop = asyncio.get_running_loop()
    async with Connector(loop=loop) as connector:
        # Create connection to Cloud SQL database.
        conn: asyncpg.Connection = await connector.connect_async(
            f"{project_id}:{region}:{instance_name}",  # Cloud SQL instance connection name
            "asyncpg",
            user=f"{database_user}",
            password=f"{database_password}",
            db=f"{database_name}",
        )

        await register_vector(conn)
        # Find similar products to the query using cosine similarity search
        # over all vector embeddings. This new feature is provided by `pgvector`.
        # Assuming `doi_list` is your list of DOI values to filter on

        # Convert the list of DOIs into a string format suitable for SQL
        boi_placeholders = ', '.join(f"${i+2}" for i in range(len(bois)))

        results = await conn.fetch(
            f"""
            SELECT doi, id, title, 1 - (embedding <=> $1) AS similarity, abstract, 
                1 - (title_embedding <=> $1) AS title_similarity
            FROM papers
            WHERE doi IN ({boi_placeholders})
            ORDER BY similarity {"DESC" if DESC else ""}
            """,
            embedding,
            *bois,  # Unpack the list of DOIs as additional arguments
        )

        if len(results) == 0:
            return []
        matches = []
        for r in results:
            # Collect the description for all the matched similar toy products.
            matches.append(Paper(*r))

        await conn.close()
        return matches

async def get_papers(query: str, nbr_of_dois:int=3) -> list[Paper]:
    """
    Retrieve Papers of relevancy based on the provided query.

    This function takes a search query as input and returns a list of papers
    that are relevant to the query. The function is designed to interface with a database or
    an external API that contains academic paper metadata.

    Args:
        query (str): A search query string that specifies the topic or keywords to search for.
                     The query should be formulated in a way that is compatible with the underlying 
                     search mechanism (e.g., keyword-based search, boolean operators, etc.).

    Returns:
        list[Paper]: A list of instances of paper corresponding to the relevant papers found.

    Raises:
        ValueError: If the query is empty or invalid.
        ConnectionError: If there is an issue connecting to the database or API.
        Exception: For any other errors encountered during the retrieval process.

    Notes:
        - Ensure that the function has access to the necessary resources (e.g., database connection,
          API credentials) to perform the query.
        - This function may involve asynchronous operations depending on the implementation.
    """
    query_embedding = await _get_embeding(query=query)
    return await _fetch_similarity(query_embedding, nbr_articles=nbr_of_dois, DESC=True)

async def _get_embeding(query: str) -> torch.Tensor:
    """
    Embed a query sentence using the Jina embedding model.

    This asynchronous function takes a query string as input and returns its embedding as a 
    NumPy array. The embedding is generated using a pre-trained Jina embedding model, which 
    transforms the input text into a numerical representation suitable for various machine 
    learning tasks.

    Args:
        query (str): The input query string that needs to be embedded. It should be a 
                     meaningful sentence or phrase to obtain a relevant embedding.

    Returns:
        np.ndarray: A NumPy array representing the embedded form of the input query. The 
                    shape and dimensions of the array depend on the specific configuration 
                    of the Jina model used.

    Raises:
        ValueError: If the query is empty or not a valid string.
        Exception: For any other errors encountered during the embedding process.

    Example:
        >>> embedding = await _get_embedding("What are the applications of machine learning?")
        >>> print(embedding.shape)
        (768,)

    Notes:
        - Ensure that the Jina embedding model is properly initialized and accessible before 
          calling this function.
        - This function is asynchronous and should be awaited in an asynchronous context.
    """
    # Tokenize the input text
    inputs = tokenizer(query, return_tensors='pt', padding=True, truncation=True)

    # Forward pass to get the embeddings
    with torch.no_grad():
        outputs = model(**inputs, task="retrieval.query")

    # Extract the last hidden states (embeddings)
    last_hidden_states = outputs.last_hidden_state

    # Optionally, get the embeddings for the [CLS] token
    cls_embedding = last_hidden_states[:, 0, :]

    return cls_embedding[0]

async def _fetch_all_citations():
    """
    Fetches all citation records from the Cloud SQL database.

    This asynchronous function connects to the Cloud SQL database and retrieves 
    all entries from the citations table. Each entry includes the source paper 
    and the papers that cite it.

    Returns:
        list[dict]: A list of dictionaries, each representing a citation record with the following keys:
            - 'source_paper' (str): The DOI of the paper being cited.
            - 'cited_by' (str): The DOI of the paper that cites the source paper.

    If no citation records are found, the function returns an empty list.

    Note:
        This function uses the pgvector extension to enable advanced vector operations,
        although it does not perform any vector-based queries in this implementation.
    """
    loop = asyncio.get_running_loop()
    async with Connector(loop=loop) as connector:
        # Create connection to Cloud SQL database.
        conn: asyncpg.Connection = await connector.connect_async(
            f"{project_id}:{region}:{instance_name}",  # Cloud SQL instance connection name
            "asyncpg",
            user=f"{database_user}",
            password=f"{database_password}",
            db=f"{database_name}",
        )

        results = await conn.fetch(
            """
            SELECT *
            FROM citations
            """
        )

        if len(results) == 0:
            return []
        matches = []
        for r in results:
            # Collect the description for all the matched similar toy products.
            matches.append(
                {
                    "source_paper": r["source_paper"],
                    "cited_by": r["cited_by"],
                }
            )

        await conn.close()
        return matches

def _bfs(bois: list[str], citations: list[dict], max_papers=10000) -> Union[list[str], list[dict]]:
    """
    Performs a breadth-first search (BFS) to explore related papers based on citations.

    This function takes a list of base of interest (BOI) papers and a list of citation data to find
    additional papers that are cited by or cite the BOI papers. The search continues until it reaches 
    a specified maximum number of papers.

    Parameters:
    - bois (list[str]): A list of DOIs (or identifiers) representing the base papers of interest.
    - citations (list[dict]): A list of citation records, where each record is a dictionary containing:
        - 'cited_by' (str): The DOI of the paper that is citing another paper.
        - 'source_paper' (str): The DOI of the paper being cited.
    - max_papers (int): The maximum number of papers to return, including the base papers and 
                        their related papers. Default is 10.

    Returns:
    - list[str]: A list of DOIs representing the base papers and any additional papers found 
                 through citations, up to the maximum specified.

    Note:
    The search stops once the total number of identified papers reaches the `max_papers` limit.
    """
    based_on = set(bois)
    future_work = set(bois)
    queue = [i for i in bois]
    citations_utalized = []
    for boi in queue:
        for citation in citations:
            if citation['cited_by'] == boi and citation['source_paper'] not in based_on:
                queue.append(citation['source_paper'])
                based_on.add(citation['source_paper'])
                citations_utalized.append(citation)
            if len(bois) + len(based_on) >= max_papers: break
        if len(bois) + len(based_on) >= max_papers: break

    queue = [i for i in bois]
    for boi in queue:
        for citation in citations:
            if citation['source_paper'] == boi  and citation['cited_by'] not in future_work:
                queue.append(citation['cited_by'])
                future_work.add(citation['cited_by'])
                citations_utalized.append(citation)
            if len(bois) + len(based_on) + len(future_work) >= max_papers: break
        if len(bois) + len(based_on) + len(future_work) >= max_papers: break
        
    return list(set(list(based_on) + list(future_work)).difference(set(bois))), citations_utalized
    
async def get_related_papers(query, bois: list[str]) -> Union[list[Paper], list[dict]]:
    """
    Retrieves related papers based on the provided list of DOIs (bois).

    This asynchronous function uses a breadth-first search (BFS) approach to
    find papers that cite the given DOIs and papers that are cited by them.

    Args:
        bois (list[str]): A list of DOIs representing the base papers for which
                          related citations are to be fetched.

    Returns:
        list[str]: A list of DOIs that are related to the provided base papers.
                    This includes the original DOIs as well as those that cite
                    or are cited by them.

    Note:
        This function calls an internal BFS function (_bfs) and fetches all
        citation data from the database using the _fetch_all_citations function.
    """
    embedding = await _get_embeding(query)
    citations = await _fetch_all_citations()
    bois, used_citations = _bfs(bois, citations)
    print("in BFS bois:",bois, used_citations)
    return await _fetch_similarity_from_list(embedding, bois), used_citations

async def main():
    await test_connection()
    # Fetch similarity for the embedding of the test query
    query = "Conditional Teacher-Student Learning"
    papers = await get_papers(query)
    print(papers)
    related, citations = await get_related_papers(query, [p.doi for p in papers])
    print(related)

if __name__ == "__main__":
    # Run the main function
    asyncio.run(main())