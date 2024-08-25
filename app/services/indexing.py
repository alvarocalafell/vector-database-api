from abc import ABC, abstractmethod
from typing import List, Tuple
import numpy as np
import heapq

class IndexingAlgorithm(ABC):
    @abstractmethod
    def build(self, vectors: List[np.ndarray]) -> None:
        pass

    @abstractmethod
    def search(self, query: np.ndarray, k: int) -> List[Tuple[int, float]]:
        pass
    

class KDTree(IndexingAlgorithm):
    def __init__(self):
        self.root = None
        self.vectors = None

    def build(self, vectors: List[np.ndarray]) -> None:
        self.vectors = vectors
        if vectors:
            self.root = self._build_tree(list(range(len(vectors))), vectors, 0)
        else:
            self.root = None

    def _build_tree(self, indices, vectors, depth):
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
        def knn_search(node, point, k, heap=None):
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
    def __init__(self):
        self.root = None
        self.vectors = None

    def build(self, vectors: List[np.ndarray]) -> None:
        self.vectors = vectors
        if vectors:
            self.root = self._build_tree(list(range(len(vectors))), vectors)
        else:
            self.root = None
        
    def _build_tree(self, indices, vectors, depth=0, max_depth=20):
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
        def knn_search(node, point, k, heap=None):
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
    def __init__(self):
        self.vectors = None

    def build(self, vectors: List[np.ndarray]) -> None:
        self.vectors = vectors

    def search(self, query: np.ndarray, k: int) -> List[Tuple[int, float]]:
        if not self.vectors:
            return []
        distances = [np.linalg.norm(query - v) for v in self.vectors]
        indices = sorted(range(len(distances)), key=lambda i: distances[i])[:k]
        return [(idx, distances[idx]) for idx in indices]