import heapq

from .count_min import CountMinSketch


class TopK:
    def __init__(self, k, width, depth, seed=0):
        self.k = k
        self.sketch = CountMinSketch(width, depth, seed)
        self.candidates = {}
        self.heap = []

    def update(self, item):
        self.sketch.update(item)
        est = self.sketch.estimate(item)
        if item in self.candidates:
            self.candidates[item] = est
        elif len(self.candidates) < self.k:
            self.candidates[item] = est
            heapq.heappush(self.heap, (est, item))
        else:
            while self.heap[0][0] != self.candidates[self.heap[0][1]]:
                stale = self.heap[0][1]
                heapq.heapreplace(self.heap, (self.candidates[stale], stale))
            if est > self.heap[0][0]:
                _, evicted = heapq.heapreplace(self.heap, (est, item))
                del self.candidates[evicted]
                self.candidates[item] = est

    def top(self):
        ranked = [(item, self.sketch.estimate(item)) for item in self.candidates]
        ranked.sort(key=lambda pair: (-pair[1], pair[0]))
        return ranked
