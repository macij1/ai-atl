# I-Cite

Welcome to **I-Cite**, an application designed for researchers and scholars to explore academic papers, retrieve relevant information, and perform text matching queries efficiently.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Functionality](#functionality)
- [Google Cloud Integration](#google-cloud-integration)
- [Jina Embeddings Model](#jina-embeddings-model)
- [Contributing](#contributing)
- [License](#license)

## Features

- Search for papers based on DOIs and keywords.
- Query papers with specific substrings in titles.
- Text matching capabilities to find relevant papers based on provided text.
- User-friendly interface built with Streamlit.

## Installation

To run the application locally, follow these steps:

1. **Clone the repository:**

   ```bash
   git clone https://github.com/macij1/i-cite.git
   cd i-cite
   ```

2. **Set up your database connection parameters in a `.env` file.**

   Your .env should follow the template below. Make sure to replace all of the values with your actual database connection parameters. You can follow the steps [here](https://cloud.google.com/sql/docs/postgres/editions-intro)
   ```bash
   DATABASE_PASSWORD=<your-db-password>
   CREDENTIALS_PATH=<your-credentials-path>
   PROJECT_ID=<your-google-project-id>
   DATABASE_USER=<your-database-user-id>
   CLAUDE_API_KEY=<your-claude-api-key>
   ```

4. **Install the required dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

5. **Set up your database connection parameters in a `.env` file.**

    ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
    
6. **Run the application:**

   ```bash
   streamlit run src/main_page.py
   ```

## Usage

- Launch the app by navigating to the provided URL in your terminal after running the command above.
- Use the buttons on the main page to navigate to different functionalities, including:
  - **Search:** Enter a DOI or keyword to find related papers.
  - **Query:** Fetch papers based on specific queries.
  - **Text Matching:** Input text to find relevant papers through substring matching.

## Functionality

### Pages

- **Main Page:** Landing page with navigation options.
- **Search Page:** Search for papers using DOIs or keywords.
- **Query Page:** Run specific queries against the database.
- **Text Matching Page:** Perform substring matching to find relevant titles.

### Example Functionality

- **Text Matching:** Allows users to input a substring to find all papers with matching titles.

## Google Cloud Integration

I-Cite leverages Google Cloud services to host a PostgreSQL instance, enabling efficient storage and retrieval of academic papers. By utilizing Cloud SQL, the application ensures scalability and reliability for handling user queries and data management.

### Steps to Set Up Google Cloud SQL:

1. Create a Cloud SQL instance on Google Cloud.
2. Configure database parameters in the `.env` file to connect to the instance.
3. Ensure appropriate permissions are set for your application to access the database.

## Jina Embeddings Model

The application utilizes the Jina embeddings model to support specialized retrieval-augmented generation (RAG). The process involves:

1. **Decomposing Abstracts:** Each abstract is broken down into meaningful components.
2. **Embedding:** The decomposed abstracts are embedded using the Jina model, creating vector representations.
3. **Similarity Search:** When a user makes a request, the system compares the input against these embeddings to find the most relevant papers based on cosine similarity.

This approach enhances the application's ability to retrieve contextually relevant information efficiently.

## Contributing

We welcome contributions to improve the I-Cite project! To contribute:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Commit your changes and push to your branch.
4. Create a pull request with a description of your changes.

### Acknowledgements

This repository was developed as part of the **AI ATL 2024 Hackathon**. Our team aimed to create an innovative tool for citation analysis and research paper discovery. The project showcases our efforts to leverage advanced technologies and machine learning techniques for academic purposes. Thank you to all our collaborators and sponsors. Thank you to arXiv for use of its open access interoperability.

For more information about the hackathon, visit the [AI ATL Hackathon website](https://ai-atl-24.devpost.com/submissions/search?page=4&sort=alpha&terms=&utf8=%E2%9C%93).

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
