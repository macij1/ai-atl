import arxiv
import json
import tarfile
# import requests
import os
import shutil


# Function to search arXiv using IDs
def search_arxiv_by_id(ids, client):
    search = arxiv.Search(
        id_list=ids,
        max_results=len(ids),
    )
    results = []
    for r in client.results(search):
        results.append(r)
    return results


def extract_tex_files(tar_path, extract_path='.', max_retries=5):
    """Extract .tex files from a tar.gz archive and return a list of extracted file paths."""
    tex_file_paths = []  # List to store paths of extracted .tex files
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            with tarfile.open(tar_path, 'r:gz') as tar:
                for member in tar.getmembers():
                    if member.name.endswith('.tex'):
                        try:
                            tar.extract(member, path=extract_path)
                            print(f'Extracted: {member.name}')
                            
                            file_path = os.path.join(extract_path, member.name)
                            tex_file_paths.append(file_path)  # Add extracted file path to list
                        except Exception as e:
                            print(f'Error processing {member.name}: {e}')
            break  # Exit loop if successful
        except Exception as e:
            retry_count += 1
            print(f'Attempt {retry_count} failed: {e}')
            if retry_count >= max_retries:
                print("Max retries reached. Exiting.")
    
    return tex_file_paths  # Return the list of extracted .tex files

def get_whole_documents(ids):
    client = arxiv.Client()
    arxiv_results = search_arxiv_by_id(ids, client)
    dirpath = "./data/extracted_data"
    
    all_tex_file_paths = []  # List to accumulate all extracted .tex file paths

    for i, paper in enumerate(arxiv_results, start=1):
        filename = f"d{i}.tar.gz"
        paper.download_source(dirpath=dirpath, filename=filename)
        print(f'Downloaded: {filename}')
        
        # Extract .tex files and get their paths
        tex_file_paths = extract_tex_files(os.path.join(dirpath, filename), extract_path=dirpath)
        all_tex_file_paths.extend(tex_file_paths)  # Append to the main list
        
        print(f'Extracted {len(tex_file_paths)} .tex files from {filename}')

    return all_tex_file_paths  # Return the list of all extracted .tex file paths


