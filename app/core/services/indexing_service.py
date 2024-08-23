from abc import ABC, abstractmethod
from typing import List, Tuple
import numpy as np
from ..entities.chunk import Chunk

class IndexingAlgorithm(ABC):
    @abstractmethod
    def build_index(self, chunks: List[Chunk]):
        pass

    @abstractmethod
    def search(self, query_vector: List[float], k: int) -> List[Tuple[Chunk, float]]:
        pass

class LinearSearch(IndexingAlgorithm):
    def __init__(self):
        self.chunks = []

    def build_index(self, chunks: List[Chunk]):
        self.chunks = chunks

    def search(self, query_vector: List[float], k: int) -> List[Tuple[Chunk, float]]:
        distances = [(chunk, np.linalg.norm(np.array(chunk.embedding) - np.array(query_vector))) 
                     for chunk in self.chunks]
        return sorted(distances, key=lambda x: x[1])[:k]

class KDTreeNode:
    def __init__(self, chunk: Chunk, left=None, right=None):
        self.chunk = chunk
        self.left = left
        self.right = right

class KDTree(IndexingAlgorithm):
    def __init__(self):
        self.root = None

    def build_index(self, chunks: List[Chunk]):
        def build_tree(chunks, depth=0):
            if not chunks:
                return None

            k = len(chunks[0].embedding)
            axis = depth % k

            sorted_chunks = sorted(chunks, key=lambda x: x.embedding[axis])
            median = len(sorted_chunks) // 2

            return KDTreeNode(
                sorted_chunks[median],
                left=build_tree(sorted_chunks[:median], depth + 1),
                right=build_tree(sorted_chunks[median + 1:], depth + 1)
            )

        self.root = build_tree(chunks)

    def search(self, query_vector: List[float], k: int) -> List[Tuple[Chunk, float]]:
        def distance(a, b):
            return np.linalg.norm(np.array(a) - np.array(b))

        def search_knn(node, query, k, depth=0, best=None):
            if node is None:
                return best

            best = best or []
            k_dim = len(query)
            axis = depth % k_dim

            next_best = best + [(node.chunk, distance(node.chunk.embedding, query))]
            next_best = sorted(next_best, key=lambda x: x[1])[:k]

            if len(next_best) < k or abs(query[axis] - node.chunk.embedding[axis]) < next_best[-1][1]:
                if query[axis] < node.chunk.embedding[axis]:
                    next_best = search_knn(node.left, query, k, depth + 1, next_best)
                    next_best = search_knn(node.right, query, k, depth + 1, next_best)
                else:
                    next_best = search_knn(node.right, query, k, depth + 1, next_best)
                    next_best = search_knn(node.left, query, k, depth + 1, next_best)

            return next_best

        return search_knn(self.root, query_vector, k)


class IndexingService:
    def __init__(self, algorithm: str = "linear"):
        self.set_algorithm(algorithm)
        self.indexed_chunks: List[Chunk] = []

    def set_algorithm(self, algorithm: str) -> None:
        if algorithm == "linear":
            self.algorithm = LinearSearch()
        elif algorithm == "kd_tree":
            self.algorithm = KDTree()
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")

    def index_chunks(self, chunks: List[Chunk]) -> None:
        self.indexed_chunks = chunks
        self.algorithm.build_index(chunks)

    def search(self, query_vector: List[float], k: int) -> List[Tuple[Chunk, float]]:
        if not self.indexed_chunks:
            raise ValueError("No chunks have been indexed yet")
        return self.algorithm.search(query_vector, k)

    def add_chunk(self, chunk: Chunk) -> None:
        self.indexed_chunks.append(chunk)
        self.algorithm.build_index(self.indexed_chunks)  # Re-index with the new chunk

    def remove_chunk(self, chunk_id: str) -> None:
        self.indexed_chunks = [chunk for chunk in self.indexed_chunks if chunk.id != chunk_id]
        self.algorithm.build_index(self.indexed_chunks)  # Re-index after removal