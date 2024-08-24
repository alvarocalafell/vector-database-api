import os
from dotenv import load_dotenv
import cohere
from typing import List

load_dotenv()  # This loads the variables from .env

cohere_api_key = os.environ.get('COHERE_API_KEY')

if not cohere_api_key:
    raise ValueError("COHERE_API_KEY environment variable is not set")

co = cohere.Client(cohere_api_key)

def get_cohere_embedding(text: str) -> List[float]:
    response = co.embed(
        texts=[text],
        model='embed-english-v2.0',
        input_type='search_query'
    )
    return response.embeddings[0]