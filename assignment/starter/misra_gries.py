class MisraGries:
    def __init__(self, k):
        self.k = k
        raise NotImplementedError("TODO 1: create the dictionary that will hold at most k-1 counters")

    def update(self, item):
        raise NotImplementedError("TODO 2: process one stream item (increment, insert, or decrement all counters)")

    def estimate(self, item):
        raise NotImplementedError("TODO 3: return the counter of item, or 0 if item is not tracked")

    def heavy_hitters(self):
        raise NotImplementedError("TODO 4: return a dict mapping each tracked item to its counter")
