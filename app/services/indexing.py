from abc import ABC, abstractmethod
from typing import List, Tuple
import numpy as np
import heapq

class IndexingAlgorithm(ABC):
    """
    Abstract base class for indexing algorithms.

    This class defines the interface for all indexing algorithms used in the vector database.
    Subclasses must implement the build and search methods.
    """

    @abstractmethod
    def build(self, vectors: List[np.ndarray]) -> None:
        """
        Build the index from a list of vectors.

        Args:
            vectors (List[np.ndarray]): List of vectors to index.
        """
        pass

    @abstractmethod
    def search(self, query: np.ndarray, k: int) -> List[Tuple[int, float]]:
        """
        Search the index for the k nearest neighbors of the query vector.

        Args:
            query (np.ndarray): Query vector.
            k (int): Number of nearest neighbors to return.

        Returns:
            List[Tuple[int, float]]: List of tuples containing the index and distance of the k nearest neighbors.
        """
        pass

class KDTree(IndexingAlgorithm):
    """
    KD-Tree implementation for efficient nearest neighbor search in low to medium dimensions.
    """

    def __init__(self):
        self.root = None
        self.vectors = None

    def build(self, vectors: List[np.ndarray]) -> None:
        """
        Build the KD-Tree from a list of vectors.

        Args:
            vectors (List[np.ndarray]): List of vectors to index.
        """
        self.vectors = vectors
        if vectors:
            self.root = self._build_tree(list(range(len(vectors))), vectors, 0)
        else:
            self.root = None

    def _build_tree(self, indices: List[int], vectors: List[np.ndarray], depth: int) -> dict:
        """
        Recursively build the KD-Tree.

        Args:
            indices (List[int]): List of indices of vectors to consider.
            vectors (List[np.ndarray]): List of all vectors.
            depth (int): Current depth in the tree.

        Returns:
            dict: A node in the KD-Tree.
        """
        if not indices:
            return None

        k = len(vectors[0])
        axis = depth % k

        sorted_indices = sorted(indices, key=lambda i: vectors[i][axis])
        median = len(sorted_indices) // 2

        return {
            'index': sorted_indices[median],
            'left': self._build_tree(sorted_indices[:median], vectors, depth + 1),
            'right': self._build_tree(sorted_indices[median + 1:], vectors, depth + 1)
        }

    def search(self, query: np.ndarray, k: int) -> List[Tuple[int, float]]:
        """
        Search the KD-Tree for the k nearest neighbors of the query vector.

        Args:
            query (np.ndarray): Query vector.
            k (int): Number of nearest neighbors to return.

        Returns:
            List[Tuple[int, float]]: List of tuples containing the index and distance of the k nearest neighbors.
        """
        def knn_search(node: dict, point: np.ndarray, k: int, heap: List[Tuple[float, int]] = None) -> List[Tuple[float, int]]:
            if heap is None:
                heap = []

            if node is None:
                return heap

            dist = np.linalg.norm(point - self.vectors[node['index']])

            if len(heap) < k:
                heapq.heappush(heap, (-dist, node['index']))
            elif dist < -heap[0][0]:
                heapq.heappushpop(heap, (-dist, node['index']))

            axis = len(heap) % len(point)
            diff = point[axis] - self.vectors[node['index']][axis]
            close, away = (node['left'], node['right']) if diff < 0 else (node['right'], node['left'])

            knn_search(close, point, k, heap)

            if len(heap) < k or abs(diff) < -heap[0][0]:
                knn_search(away, point, k, heap)

            return heap

        results = knn_search(self.root, query, k)
        return [(idx, -dist) for dist, idx in sorted(results, key=lambda x: (-x[0], x[1]))]

class BallTree(IndexingAlgorithm):
    """
    Ball Tree implementation for efficient nearest neighbor search in high dimensions.
    """

    def __init__(self):
        self.root = None
        self.vectors = None

    def build(self, vectors: List[np.ndarray]) -> None:
        """
        Build the Ball Tree from a list of vectors.

        Args:
            vectors (List[np.ndarray]): List of vectors to index.
        """
        self.vectors = vectors
        if vectors:
            self.root = self._build_tree(list(range(len(vectors))), vectors)
        else:
            self.root = None

    def _build_tree(self, indices: List[int], vectors: List[np.ndarray], depth: int = 0, max_depth: int = 20) -> dict:
        """
        Recursively build the Ball Tree.

        Args:
            indices (List[int]): List of indices of vectors to consider.
            vectors (List[np.ndarray]): List of all vectors.
            depth (int): Current depth in the tree.
            max_depth (int): Maximum depth of the tree.

        Returns:
            dict: A node in the Ball Tree.
        """
        if not indices or depth >= max_depth:
            return None

        center = np.mean([vectors[i] for i in indices], axis=0)
        radius = max(np.linalg.norm(vectors[i] - center) for i in indices)

        return {
            'center': center,
            'radius': radius,
            'index': indices[0],
            'left': self._build_tree(indices[:len(indices)//2], vectors, depth+1, max_depth),
            'right': self._build_tree(indices[len(indices)//2:], vectors, depth+1, max_depth)
        }

    def search(self, query: np.ndarray, k: int) -> List[Tuple[int, float]]:
        """
        Search the Ball Tree for the k nearest neighbors of the query vector.

        Args:
            query (np.ndarray): Query vector.
            k (int): Number of nearest neighbors to return.

        Returns:
            List[Tuple[int, float]]: List of tuples containing the index and distance of the k nearest neighbors.
        """
        def knn_search(node: dict, point: np.ndarray, k: int, heap: List[Tuple[float, int]] = None) -> List[Tuple[float, int]]:
            if heap is None:
                heap = []

            if node is None:
                return heap

            dist = np.linalg.norm(point - node['center'])

            if len(heap) < k:
                heapq.heappush(heap, (-dist, node['index']))
            elif dist < -heap[0][0]:
                heapq.heappushpop(heap, (-dist, node['index']))

            if len(heap) < k or dist - node['radius'] < -heap[0][0]:
                knn_search(node['left'], point, k, heap)
                knn_search(node['right'], point, k, heap)

            return heap

        results = knn_search(self.root, query, k)
        return [(idx, -dist) for dist, idx in sorted(results, key=lambda x: (-x[0], x[1]))]

class BruteForce(IndexingAlgorithm):
    """
    Brute Force implementation for exact nearest neighbor search.
    """

    def __init__(self):
        self.vectors = None

    def build(self, vectors: List[np.ndarray]) -> None:
        """
        Store the vectors for brute force search.

        Args:
            vectors (List[np.ndarray]): List of vectors to index.
        """
        self.vectors = vectors

    def search(self, query: np.ndarray, k: int) -> List[Tuple[int, float]]:
        """
        Perform a brute force search for the k nearest neighbors of the query vector.

        Args:
            query (np.ndarray): Query vector.
            k (int): Number of nearest neighbors to return.

        Returns:
            List[Tuple[int, float]]: List of tuples containing the index and distance of the k nearest neighbors.
        """
        if not self.vectors:
            return []
        distances = [np.linalg.norm(query - v) for v in self.vectors]
        indices = sorted(range(len(distances)), key=lambda i: distances[i])[:k]
        return [(idx, distances[idx]) for idx in indices]