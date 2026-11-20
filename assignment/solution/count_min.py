import random

from hashing import UniversalHash


class CountMinSketch:
    def __init__(self, width, depth, seed=0):
        rng = random.Random(seed)
        self.width = width
        self.depth = depth
        self.hashes = [UniversalHash(width, rng) for _ in range(depth)]
        self.table = [[0] * width for _ in range(depth)]

    def update(self, item):
        for row, h in zip(self.table, self.hashes):
            row[h(item)] += 1

    def estimate(self, item):
        return min(row[h(item)] for row, h in zip(self.table, self.hashes))
