from abc import ABC, abstractmethod
from typing import List, Tuple
import numpy as np
import logging
import time

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class VectorIndex(ABC):
    @abstractmethod
    def build(self, vectors: List[np.ndarray]) -> None:
        pass

    @abstractmethod
    def search(self, query: np.ndarray, k: int) -> List[Tuple[int, float]]:
        pass

class KDTree(VectorIndex):
    def __init__(self):
        self.root = None
        self.vectors = None

    def build(self, vectors: List[np.ndarray]) -> None:
        logger.debug(f"Entering KDTree build method with {len(vectors)} vectors")
        start_time = time.time()
        self.vectors = vectors
        
        def build_tree(points, depth=0):
            logger.debug(f"Building tree at depth {depth} with {len(points)} points")
            if not points:
                logger.debug("No points, returning None")
                return None

            k = len(points[0])
            axis = depth % k

            logger.debug(f"Sorting points on axis {axis}")
            points.sort(key=lambda x: x[axis])
            median = len(points) // 2

            logger.debug(f"Creating node at median {median}")
            return {
                'point': points[median],
                'left': build_tree(points[:median], depth + 1),
                'right': build_tree(points[median + 1:], depth + 1)
            }

        logger.debug("Starting to build the tree")
        self.root = build_tree(vectors)
        logger.debug(f"KDTree built in {time.time() - start_time:.2f} seconds")

    def search(self, query: np.ndarray, k: int) -> List[Tuple[int, float]]:
        logger.debug(f"Entering KDTree search method for {k} nearest neighbors")
        start_time = time.time()
        def distance(a, b):
            return np.linalg.norm(np.array(a) - np.array(b))

        def knn_search(node, point, k, depth=0, heap=None):
            if node is None:
                return heap

            if heap is None:
                heap = []

            dist = distance(point, node['point'])
            if len(heap) < k:
                heap.append((-dist, node['point']))
                heap.sort(reverse=True)
            elif dist < -heap[0][0]:
                heap[0] = (-dist, node['point'])
                heap.sort(reverse=True)

            axis = depth % len(point)
            diff = point[axis] - node['point'][axis]
            close, away = (node['left'], node['right']) if diff < 0 else (node['right'], node['left'])

            knn_search(close, point, k, depth + 1, heap)

            if len(heap) < k or abs(diff) < -heap[0][0]:
                knn_search(away, point, k, depth + 1, heap)

            return heap

        logger.debug(f"KDTree search completed in {time.time() - start_time:.2f} seconds")
        results = knn_search(self.root, query, k)
        return [(int(np.where((np.array(self.vectors) == r[1]).all(axis=1))[0][0]), -r[0]) for r in results]

class BallTree(VectorIndex):
    def __init__(self):
        self.root = None

    def build(self, vectors: List[np.ndarray]) -> None:
        def build_tree(points):
            if len(points) == 1:
                return {'center': points[0], 'radius': 0, 'index': 0, 'left': None, 'right': None}

            center = np.mean(points, axis=0)
            radius = max(np.linalg.norm(p - center) for p in points)
            
            left_points = points[:len(points)//2]
            right_points = points[len(points)//2:]

            return {
                'center': center,
                'radius': radius,
                'left': build_tree(left_points),
                'right': build_tree(right_points)
            }

        self.root = build_tree(vectors)

    def search(self, query: np.ndarray, k: int) -> List[Tuple[int, float]]:
        def distance(a, b):
            return np.linalg.norm(np.array(a) - np.array(b))

        def knn_search(node, point, k, heap=None):
            if heap is None:
                heap = []

            if node is None:
                return heap

            dist = distance(point, node['center'])

            if len(heap) < k:
                heap.append((-dist, node['index']))
                heap.sort(reverse=True)
            elif dist < -heap[0][0]:
                heap[0] = (-dist, node['index'])
                heap.sort(reverse=True)

            if node['left'] is None and node['right'] is None:
                return heap

            if len(heap) < k or dist - node['radius'] < -heap[0][0]:
                knn_search(node['left'], point, k, heap)
                knn_search(node['right'], point, k, heap)

            return heap

        results = knn_search(self.root, query, k)
        return [(r[1], -r[0]) for r in results]

class BruteForce(VectorIndex):
    def __init__(self):
        self.vectors = []

    def build(self, vectors: List[np.ndarray]) -> None:
        logger.debug(f"Building BruteForce index with {len(vectors)} vectors")
        self.vectors = vectors

    def search(self, query: np.ndarray, k: int) -> List[Tuple[int, float]]:
        logger.debug(f"Performing BruteForce search for {k} nearest neighbors")
        distances = [(i, np.linalg.norm(query - vec)) for i, vec in enumerate(self.vectors)]
        distances.sort(key=lambda x: x[1])
        return distances[:k]