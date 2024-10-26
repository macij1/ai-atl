import json
import time
import arxiv
import os

def download_arxiv_sources_with_client(json_file_path):
    client = arxiv.Client()
    
    # Ensure the download directory exists
    download_dir = './data/papers'
    
    # Load the JSON data
    with open(json_file_path, 'r') as file:
        data = json.load(file)  # Now `data` is expected to be a list of dictionaries
    
    # Iterate over each paper entry in the list
    for paper_info in data:
        arxiv_id = paper_info["id"]

        # Use arxiv.Client to retrieve paper metadata
        try:
            paper = next(client.results(arxiv.Search(id_list=[arxiv_id])), None)
            
            if paper:
                # Download with custom directory path
                paper.download_source(dirpath=download_dir)
                print(f"Downloaded {arxiv_id} to {download_dir}")
                
            else:
                print(f"No results found for arXiv ID {arxiv_id}")

        except Exception as e:
            print(f"Error downloading {arxiv_id}: {e}")

# Usage
download_arxiv_sources_with_client('./data/ml_papers.json')
