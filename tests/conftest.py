import pytest
from dotenv import load_dotenv
import os

@pytest.fixture(scope="session", autouse=True)
def load_env():
    load_dotenv()
    if "COHERE_API_KEY" not in os.environ:
        pytest.fail("COHERE_API_KEY not found in environment variables")

@pytest.fixture
def cohere_api_key():
    return os.environ.get("COHERE_API_KEY")