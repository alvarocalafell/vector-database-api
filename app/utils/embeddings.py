import os
from dotenv import load_dotenv
import cohere

load_dotenv()  # This loads the variables from .env

cohere_api_key = os.environ.get('COHERE_API_KEY')

if not cohere_api_key:
    raise ValueError("COHERE_API_KEY environment variable is not set")

co = cohere.Client(cohere_api_key)

def get_embedding(text: str) -> list[float]:
    """Generate an embedding for the given text using Cohere."""
    response = co.embed(
        texts=[text],
        model='small',
        truncate='END'
    )
    return response.embeddings[0]