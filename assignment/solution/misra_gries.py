class MisraGries:
    def __init__(self, k):
        self.k = k
        self.counters = {}

    def update(self, item):
        counters = self.counters
        if item in counters:
            counters[item] += 1
        elif len(counters) < self.k - 1:
            counters[item] = 1
        else:
            for key in list(counters):
                counters[key] -= 1
                if counters[key] == 0:
                    del counters[key]

    def estimate(self, item):
        return self.counters.get(item, 0)

    def heavy_hitters(self):
        return dict(self.counters)
