import json
import requests
import arxiv

def download_arxiv_sources_with_client(json_file_path):
    client = arxiv.Client()
    
    # Load the JSON data
    with open(json_file_path, 'r') as file:
        data = json.load(file)  # Now `data` is expected to be a list of dictionaries
    
    # Iterate over each paper entry in the list
    for paper_info in data:
        arxiv_id = paper_info["id"]

        # Use arxiv.Client to retrieve paper metadata
        paper = next(arxiv.Client().results(arxiv.Search(id_list=[arxiv_id])))
        paper.download_source()
        
        if paper:
            # Construct the download URL for the source
            download_url = f'https://arxiv.org/e-print/{arxiv_id}'
            
            # Download the .tar.gz file
            response = requests.get(download_url)
            
            if response.status_code == 200:
                filename = f"{arxiv_id.replace('/', '_')}.tar.gz"
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"Downloaded {filename} successfully.")
            else:
                print(f"Failed to download source for {arxiv_id}")
        else:
            print(f"No results found for arXiv ID {arxiv_id}")

# Usage
download_arxiv_sources_with_client('ml_papers.json')
