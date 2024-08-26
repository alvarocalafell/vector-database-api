# Vector Database API

## Project Overview
This project implements a high-performance REST API for a Vector Database using FastAPI. It allows users to manage libraries, documents, and chunks, as well as perform efficient k-Nearest Neighbor (k-NN) vector searches. The API is designed with a focus on scalability, maintainability, and adherence to SOLID principles.

## Key Features
1. CRUD operations for libraries, documents, and chunks
2. Efficient indexing of library contents
3. k-Nearest Neighbor vector search functionality
4. Support for multiple indexing algorithms (KD-Tree and Ball Tree)

## Technical Stack
- **Framework**: FastAPI
- **Data Validation**: Pydantic
- **Containerization**: Docker
- **Orchestration**: Kubernetes
- **Package Management**: Helm
- **Testing**: pytest
- **CI/CD**: GitHub Actions

## Code Quality Highlights
- **SOLID Principles**: The codebase is structured to adhere to SOLID design principles, promoting modularity and maintainability.
- **Static Typing**: Extensive use of type hints throughout the codebase for improved code clarity and error prevention.
- **FastAPI Best Practices**: Utilizes FastAPI's dependency injection, Pydantic models, and asynchronous request handling.
- **Modularity**: The project is organized into distinct modules for improved reusability and separation of concerns.
- **RESTful API Design**: Endpoints follow RESTful conventions for intuitive API usage.
- **Error Handling**: Comprehensive error handling with custom exceptions and informative error messages.
- **Testing**: Extensive test suite covering unit tests, integration tests, and API endpoint tests.

## Installation and Setup

### Local Development
1. Clone the repository:
   ```
   git clone https://github.com/alvarocalafell/vector-database-api.git
   cd vector-database-api
   ```
2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Set up environment variables:
   ```
   cp .env.example .env
   # Edit .env with your configuration
   ```
5. Run the application:
   ```
   uvicorn app.main:app --reload
   ```

### Docker Deployment
1. Build the Docker image:
   ```
   docker build -t vector-db-api:latest .
   ```
2. Run the container:
   ```
   docker run -p 8000:8000 vector-db-api:latest
   ```

### Kubernetes Deployment
1. Build and load the Docker image into Minikube:
   ```
   eval $(minikube docker-env)
   docker build -t vector-db-api:latest .
   ```
2. Install the Helm chart:
   ```
   helm install vector-db-api ./helm/vector-db-api
   ```
3. Access the API:
   ```
   minikube service vector-db-api --url
   ```

## API Documentation

### Libraries
- `GET /api/v1/libraries/`: List all libraries
- `POST /api/v1/libraries/`: Create a new library
- `GET /api/v1/libraries/{library_id}`: Retrieve a specific library
- `PUT /api/v1/libraries/{library_id}`: Update a library
- `DELETE /api/v1/libraries/{library_id}`: Delete a library

### Documents
- `GET /api/v1/documents/{library_id}`: List all documents in a library
- `POST /api/v1/documents/{library_id}`: Add a document to a library
- `GET /api/v1/documents/{library_id}/{document_id}`: Retrieve a specific document
- `PUT /api/v1/documents/{library_id}/{document_id}`: Update a document
- `DELETE /api/v1/documents/{library_id}/{document_id}`: Delete a document

### Chunks
- `GET /api/v1/chunks/{library_id}/{document_id}`: List all chunks in a document
- `POST /api/v1/chunks/{library_id}/{document_id}`: Add a chunk to a document
- `GET /api/v1/chunks/{library_id}/{document_id}/{chunk_id}`: Retrieve a specific chunk
- `PUT /api/v1/chunks/{library_id}/{document_id}/{chunk_id}`: Update a chunk
- `DELETE /api/v1/chunks/{library_id}/{document_id}/{chunk_id}`: Delete a chunk

### Search
- `GET /api/v1/search/`: List available search methods
- `POST /api/v1/search/{library_id}/knn`: Perform k-NN search in a library
- `POST /api/v1/search/{library_id}/cosine`: Perform cosine similarity search in a library

## Testing
Run the test suite using pytest:
```
pytest tests/
```

## CI/CD
The project uses GitHub Actions for continuous integration and deployment. The workflow includes:
- Running tests
- Linting and code quality checks
- Building and pushing Docker images
- Deployment to staging/production environments

## Indexing Algorithms

This project implements three indexing algorithms for vector search: KD-Tree, Ball Tree, and Brute Force. Each algorithm is implemented from scratch without relying on external libraries, allowing for a deep understanding of their mechanics and trade-offs.

### 1. KD-Tree (K-Dimensional Tree)

#### Implementation:
The KD-Tree is implemented as a binary tree where each node represents a point in k-dimensional space. The tree is constructed by recursively partitioning the space along different dimensions.

#### Complexities:
- Construction: O(n log n), where n is the number of points
- Search (best and average case): O(log n)
- Search (worst case): O(n)
- Space: O(n)

#### Rationale:
KD-Tree is chosen for its efficiency in low to medium dimensional spaces (typically < 20 dimensions). It performs well for exact nearest neighbor searches and can be more memory-efficient than some other structures. The logarithmic search time in average cases makes it suitable for fast similarity searches in our vector database.

### 2. Ball Tree

#### Implementation:
The Ball Tree is implemented as a binary tree where each node represents a hypersphere containing a subset of points. The tree is constructed by recursively partitioning the space into nested hyperspheres.

#### Complexities:
- Construction: O(n log n)
- Search (best and average case): O(log n)
- Search (worst case): O(n)
- Space: O(n)

#### Rationale:
Ball Tree is particularly effective for high-dimensional data where KD-Trees may become less efficient. It adapts better to the intrinsic dimensionality of the data, making it a good choice for our vector database which may need to handle embeddings of varying dimensions. The Ball Tree can outperform KD-Tree in higher dimensions while maintaining similar time complexities.

### 3. Brute Force (Baseline)

#### Implementation:
The Brute Force method simply stores all vectors and performs a linear search through all points for each query.

#### Complexities:
- Construction: O(n)
- Search: O(n)
- Space: O(n)

#### Rationale:
While not efficient for large datasets, the Brute Force method serves as an important baseline for comparison. It guarantees finding the exact nearest neighbors and is useful for validating the results of more sophisticated algorithms. In small datasets or in very high dimensional spaces, Brute Force can sometimes outperform tree-based methods due to its simplicity and cache-friendly linear access pattern.

### Comparison and Choice

The choice between these algorithms depends on several factors:

1. **Dimensionality**: For lower dimensions (typically < 20), KD-Tree often performs best. For higher dimensions, Ball Tree can be more effective.
2. **Dataset Size**: For very small datasets, Brute Force can be faster due to its simplicity.
3. **Query Time vs. Build Time**: KD-Tree and Ball Tree have higher build times but faster query times for large datasets, while Brute Force has negligible build time but slower query times.
4. **Exact vs. Approximate**: All three methods provide exact results, but tree-based methods can be modified for approximate searches if needed.

In our implementation, we provide all three options to allow flexibility depending on the specific use case and data characteristics. Users can choose the most appropriate index for their needs, with KD-Tree as the default for its good all-around performance in many common scenarios.

By implementing these algorithms from scratch, we gain a deeper understanding of their workings and can fine-tune them specifically for our vector database use case. This approach also allows us to maintain full control over the implementation, enabling easier debugging and potential optimizations in the future.

## License
This project is licensed under the MIT License.