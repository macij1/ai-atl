# anthropic_client.py

import anthropic

class AnthropicClient:
    def __init__(self, api_key):
        self.client = anthropic.Client(api_key=api_key)

    def get_response(self, docs, question, model="claude-3-haiku-20240307", max_tokens=1000):
        prompt = (
            f"{anthropic.HUMAN_PROMPT}\
            I want you to answer the following question: {question}. I will provide you with a list of documents that are useful to answer this question.\
            \n Each document will be provided in the format. TITLE: <paper_title> DOI: <doi> DOCUMENT <document> \
            \n Think of yourself as a machine learning expert who already knew everything present in these documents. Carefully analyze the above documents and answer the following question.\
            \n Please also cite any of the documents that were given to you as context but do not make any mention of documents being provided to you. To cite a document, you would use it's DOI.\
            \n Here is your question\n \
            Question: {question}{anthropic.AI_PROMPT}"
        )
        
        response = self.client.messages.create(
            model=model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text