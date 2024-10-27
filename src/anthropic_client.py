# anthropic_client.py

import anthropic

class AnthropicClient:
    def __init__(self, api_key):
        self.client = anthropic.Client(api_key=api_key)

    def get_response(self, docs, question, model="claude-3-haiku-20240307", max_tokens=1000):
        prompt = (
            f"{anthropic.HUMAN_PROMPT} Here's the article:\n\n{docs}\n\n"
            f"Question: {question}{anthropic.AI_PROMPT}"
        )
        
        response = self.client.messages.create(
            model=model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text