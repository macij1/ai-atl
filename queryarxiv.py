import arxiv
import json
import tarfile
# import requests
import os

# Function to search arXiv using IDs
def search_arxiv_by_id(ids):
    search = arxiv.Search(
        id_list=ids,
        max_results=len(ids),
    )
    results = []
    for r in client.results(search):
        results.append(r)
    return results

# Extract and all tex files from the gz 
def extract_and_join_tex_files(tar_path, extract_path='.', output_file='combined.tex', max_retries=5):
    """Check if a directory exists and delete it if it does."""
    try:
        if os.path.exists(tar_path) and os.path.isdir(tar_path):
            shutil.rmtree(tar_path)  # Delete the directory and its contents
            print(f'Deleted directory: {tar_path}')
        else:
            print(f'Directory does not exist: {tar_path}')
    except Exception as e:
        print(f'Error deleting directory {tar_path}: {e}')
    retry_count = 0
    while retry_count < max_retries:
        try:
            with open(output_file, 'a') as outfile:
                with tarfile.open(tar_path, 'r:gz') as tar:
                    for member in tar.getmembers():
                        if member.name.endswith('.tex'):
                            try:
                                tar.extract(member, path=extract_path)
                                print(f'Extracted: {member.name}')
                                
                                file_path = os.path.join(extract_path, member.name)
                                #print(file_path)
                                with open(file_path, 'r') as infile:
                                    contents = infile.read()
                                    outfile.write(contents + "\n")
                                    print(f'Added: {member.name} to {output_file}')
                            except Exception as e:
                                print(f'Error processing {member.name}: {e}')
            break  # Exit loop if successful
        except Exception as e:
            retry_count += 1
            print(f'Attempt {retry_count} failed: {e}')
            if retry_count >= max_retries:
                print("Max retries reached. Exiting.")

# Unused
def get_arxiv_paper_as_html(url):

    # Send a GET request to the specified URL
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code != 200:
        print(f"Paper is not available on HTML : {response.status_code}")


    else:
        # Get the content of the web page
        page_content = response.text

        return page_content

arxiv_results = search_arxiv_by_id(ids)
dirpath = "./data/extracted_data"


for i, paper in enumerate(arxiv_results, start=1):
    # page_content = get_arxiv_paper_as_html(paper.entry_id.replace("abs", "html"))

    filename = f"d{i}.tar.gz"
    paper.download_source(dirpath=dirpath, filename=filename)
    print(i)
    # Extract the tar.gz file
    # extract_tar_gz(dirpath+'/'+filename, dirpath)
    extract_and_join_tex_files(dirpath+'/'+filename, dirpath, 'combined.tex')
    print(i)


