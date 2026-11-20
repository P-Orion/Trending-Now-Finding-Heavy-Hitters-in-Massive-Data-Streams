import random

from hashing import UniversalHash


class CountMinSketch:
    def __init__(self, width, depth, seed=0):
        self.width = width
        self.depth = depth
        raise NotImplementedError("TODO 1: build `depth` hash functions UniversalHash(width, rng) from random.Random(seed) and a depth x width table of zeros")

    def update(self, item):
        raise NotImplementedError("TODO 2: add 1 to table[row][hash_of_row(item)] for every row")

    def estimate(self, item):
        raise NotImplementedError("TODO 3: return the minimum of table[row][hash_of_row(item)] over all rows")
