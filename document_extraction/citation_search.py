import json
import pandas as pd
import subprocess
import os
import shutil
import tempfile
import sys

# Load the ML papers
ml_papers = []
with open("data/ml_papers.json", "r") as file:
    ml_papers = json.load(file)

# Extract DOIs from the papers
dois = [paper['doi'] for paper in ml_papers]

def process_doi_range(start, end):
    """Process a subset of DOIs by specifying the start and end index."""
    doi_subset = dois[start:end]
    doi_set_list = set(doi_subset)

    # Create a temporary folder to store CSVs
    output_folder = tempfile.mkdtemp()

    # Prepare a list to store citation relationships
    citation_connections = []

    def run_citation_graph(doi):
        """Run the citation_graph library and store results in a temporary folder."""
        command = f"python -m citation_graph -v -m 1000 -d=1 {doi} -g -l --list-file-name {output_folder}/output.csv"

        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Error processing DOI {doi}:\n{result.stderr}")
                return None
        except Exception as e:
            print(f"Exception occurred while processing {doi}: {e}")
            return None

        return f"{output_folder}/output.csv"

    def process_csv(csv_path):
        """Load the CSV into a DataFrame, filter for Depth 1, and delete the file."""
        if os.path.exists(csv_path):
            try:
                df = pd.read_csv(csv_path, delimiter=';')
                # Filter rows where Depth == 1
                df = df[df["Depth"] == 1]
            except Exception as e:
                print(f"Error reading {csv_path}: {e}")
                df = pd.DataFrame()  # Return empty DataFrame on failure

            os.remove(csv_path)  # Clean up after processing
            return df
        else:
            print(f"No CSV found at {csv_path}")
            return pd.DataFrame()

    # Iterate through the subset of DOIs
    for i, source_doi in enumerate(doi_subset, start=1):
        print(f"Processing DOI: {source_doi}")
        csv_path = run_citation_graph(source_doi)

        if csv_path:
            citation_df = process_csv(csv_path)

            # If citations were found, process them
            if not citation_df.empty:
                for cited_doi in citation_df["Id"].str.replace("doi::", "").dropna():
                    if cited_doi in doi_set_list:
                        citation_connections.append({
                            "source_paper": source_doi,
                            "cited_by": cited_doi
                        })

        # Print progress every 10 papers processed
        if i % 10 == 0:
            print(f"{i}/{end - start} papers completed")

    # Convert the citation connections to a DataFrame
    citation_connections_df = pd.DataFrame(citation_connections)

    # Save the results to a CSV file with the range in the file name
    output_csv = f"data/citation_connections_{start}_{end}.csv"
    citation_connections_df.to_csv(output_csv, index=False)

    print(f"Saved citation connections to {output_csv}")

    # Clean up the temporary folder
    shutil.rmtree(output_folder)

# Ensure the correct number of arguments are passed
if len(sys.argv) != 3:
    print("Usage: python script_name.py <start_index> <end_index>")
    sys.exit(1)

# Read the start and end indices from the command-line arguments
try:
    start_index = int(sys.argv[1])
    end_index = int(sys.argv[2])
except ValueError:
    print("Start and end indices must be integers.")
    sys.exit(1)

# Call the function with the provided indices
process_doi_range(start=start_index, end=end_index)
