# Vector Database API

## Project Overview
This project implements a REST API for a Vector Database, allowing users to index and query documents using vector embeddings. It supports fast similarity searches, crucial for applications in natural language processing and recommendation systems.

## Objectives
- Create, read, update, and delete libraries
- Manage documents and chunks within libraries
- Index library contents
- Perform k-Nearest Neighbor vector searches

## Installation and Setup

### Local Setup
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application: `uvicorn app.main:app --reload`

### Kubernetes Deployment
1. Build the Docker image: `docker build -t vector-db-api:latest .`
2. Load the image into Minikube: `minikube image load vector-db-api:latest`
3. Install the Helm chart: `helm install vector-db-api ./helm/vector-db-api`

## API Documentation

### Libraries
- `POST /libraries/`: Create a new library
- `GET /libraries/{library_id}`: Retrieve a library
- `PUT /libraries/{library_id}`: Update a library
- `DELETE /libraries/{library_id}`: Delete a library

### Documents
- `POST /documents/{library_id}`: Add a document to a library
- `GET /documents/{library_id}/{document_id}`: Retrieve a document
- `PUT /documents/{library_id}/{document_id}`: Update a document
- `DELETE /documents/{library_id}/{document_id}`: Delete a document

### Chunks
- `POST /chunks/{library_id}/{document_id}`: Add a chunk to a document
- `GET /chunks/{library_id}/{document_id}/{chunk_id}`: Retrieve a chunk
- `PUT /chunks/{library_id}/{document_id}/{chunk_id}`: Update a chunk
- `DELETE /chunks/{library_id}/{document_id}/{chunk_id}`: Delete a chunk

### Search
- `POST /search/{library_id}`: Perform k-NN search in a library

## Usage Examples
```python
import requests

# Create a library
response = requests.post("http://localhost:8000/libraries/", json={
    "id": "test-library",
    "documents": [],
    "metadata": {"name": "Test Library"}
})

# Add a document
response = requests.post("http://localhost:8000/documents/test-library", json={
    "id": "doc1",
    "chunks": [
        {
            "id": "chunk1",
            "text": "Sample text",
            "embedding": [0.1, 0.2, 0.3, 0.4, 0.5],
            "metadata": {"position": 1}
        }
    ],
    "metadata": {"author": "John Doe"}
})

# Perform a search
response = requests.post("http://localhost:8000/search/test-library", json={
    "query_vector": [0.1, 0.2, 0.3, 0.4, 0.5],
    "k": 1
})
```

## Technical Choices
- FastAPI for high-performance, easy-to-use API development
- Pydantic for data validation and settings management
- Custom implementations of KD-Tree and Ball Tree for vector indexing
- Docker and Kubernetes for containerization and deployment
- Helm for Kubernetes package management

## Deployment Instructions
1. Ensure Minikube is running: `minikube start`
2. Build and load the Docker image:
   ```
   eval $(minikube docker-env)
   docker build -t vector-db-api:latest .
   ```
3. Install the Helm chart:
   ```
   helm install vector-db-api ./helm/vector-db-api
   ```
4. Access the API:
   ```
   minikube service vector-db-api --url
   ```

For updates, use: `helm upgrade vector-db-api ./helm/vector-db-api`

## Indexing Algorithms Analysis

### KD-Tree

#### Time Complexity:
- Construction: O(n log n), where n is the number of points
- Search (best and average case): O(log n)
- Search (worst case): O(n)

#### Space Complexity:
- O(n)

#### Why KD-Tree?
KD-Tree is chosen for its efficiency in low to medium dimensional spaces. It performs well for exact nearest neighbor searches and can be more memory-efficient than some other structures.

### Ball Tree

#### Time Complexity:
- Construction: O(n log n)
- Search (best and average case): O(log n)
- Search (worst case): O(n)

#### Space Complexity:
- O(n)

#### Why Ball Tree?
Ball Tree is particularly effective for high-dimensional data where KD-Trees may become less efficient. It can adapt better to the intrinsic dimensionality of the data.

### Comparison and Choice
Both KD-Tree and Ball Tree offer logarithmic search time in the average case, making them suitable for efficient similarity searches. The choice between them depends on the dimensionality of your data:

- For lower dimensions (typically < 20), KD-Tree often performs better.
- For higher dimensions, Ball Tree can be more effective.

In our implementation, we provide both options to allow flexibility depending on the specific use case and data characteristics. Users can choose the most appropriate index for their needs.
