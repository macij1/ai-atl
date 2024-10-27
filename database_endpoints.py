from pgvector.asyncpg import register_vector
import asyncio
import asyncpg
from google.cloud.sql.connector import Connector
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel
import os

tokenizer = AutoTokenizer.from_pretrained('jinaai/jina-embeddings-v3')
model = AutoModel.from_pretrained('jinaai/jina-embeddings-v3', trust_remote_code=True)

project_id = os.getenv("PROJECT_ID")
database_password = os.getenv('DATABASE_PASSWORD')
region = "us-central1"
instance_name = "research-paper-db"
database_name = "research-papers"
database_user = os.getenv("DATABASE_USER")

class Paper:
    def __init__(self, doi, id=None, title=None, abstract=None, similarity=None, title_similarity=None, date=None, content=None) -> None:
        self.id = id
        self.doi = doi
        self.title = title
        self.abstract = abstract
        self.similarity = similarity
        self.title_similarity = title_similarity
        self.date = date
        self.content = content
    
    def __str__(self) -> str:
        return f"doi: {self.doi}"
    
    def __repr__(self):
        return f"doi: {self.doi}"

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

async def _fetch_similarity(embeding, nbr_articles=2, DESC=True) -> list[Paper]:
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
        results = await conn.fetch(
            f"""
            SELECT doi, title, 1 - (embedding <=> $1) AS similarity, abstract, doi, 1 - (title_embedding <=> $1) AS title_similarity, id
            FROM papers
            ORDER BY similarity {"DESC" if DESC else ""}
            LIMIT $2
            """,
            embeding,
            nbr_articles
        )

        if len(results) == 0:
            raise Exception("Did not find any results. Adjust the query parameters.")
        matches = []
        for r in results:
            # Collect the description for all the matched similar toy products.
            matches.append(Paper(*r)
            )

        await conn.close()
        return matches

async def get_dois(query: str, nbr_of_dois:int=5) -> list[str]:
    """
    Retrieve DOIs of relevant papers based on the provided query.

    This function takes a search query as input and returns a list of Digital Object Identifiers (DOIs)
    for papers that are relevant to the query. The function is designed to interface with a database or
    an external API that contains academic paper metadata.

    Args:
        query (str): A search query string that specifies the topic or keywords to search for.
                     The query should be formulated in a way that is compatible with the underlying 
                     search mechanism (e.g., keyword-based search, boolean operators, etc.).

    Returns:
        list[str]: A list of DOIs corresponding to the relevant papers found. Each DOI is a string
                    that uniquely identifies a paper in the digital environment.

    Raises:
        ValueError: If the query is empty or invalid.
        ConnectionError: If there is an issue connecting to the database or API.
        Exception: For any other errors encountered during the retrieval process.

    Example:
        >>> dois = get_dois("machine learning applications in healthcare")
        >>> print(dois)
        ['10.1234/abcd1234', '10.5678/efgh5678', ...]

    Notes:
        - Ensure that the function has access to the necessary resources (e.g., database connection,
          API credentials) to perform the query.
        - This function may involve asynchronous operations depending on the implementation.
    """
    query_embedding = _get_embeding(query=query)
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


def _bfs(bois: list[str], citations: list[dict], max_papers=10) -> list[str]:
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
    based_on = set()
    future_work = set()
    queue = [i for i in bois]
    for boi in queue:
        for citation in citations:
            if citation['cited_by'] == boi and citation['source_paper'] not in based_on:
                queue.append(citation['source_paper'])
                based_on.add(citation['source_paper'])
            if len(bois) + len(based_on) >= max_papers: break
        if len(bois) + len(based_on) >= max_papers: break

    queue = [i for i in bois]
    for boi in queue:
        for citation in citations:
            if citation['source_paper'] == boi  and citation['cited_by'] not in future_work:
                queue.append(citation['cited_by'])
                future_work.add(citation['cited_by'])
            if len(bois) + len(based_on) + len(future_work) >= max_papers: break
        if len(bois) + len(based_on) + len(future_work) >= max_papers: break
    return bois + list(based_on) + list(future_work)
    
async def get_related_bois(bois: list[str]) -> list[str]:
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
    return _bfs(bois, await _fetch_all_citations())

async def main():
    await test_connection()
    # Fetch similarity for the embedding of the test query
    similarity = await _fetch_similarity(await _get_embeding("test"))
    print(similarity)

if __name__ == "__main__":
    # Run the main function
    asyncio.run(main())