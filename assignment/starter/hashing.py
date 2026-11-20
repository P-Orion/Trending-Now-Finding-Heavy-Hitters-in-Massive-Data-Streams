PRIME = (1 << 61) - 1


class UniversalHash:
    def __init__(self, width, rng):
        self.width = width
        self.a = rng.randrange(1, PRIME)
        self.b = rng.randrange(0, PRIME)

    def __call__(self, x):
        return ((self.a * x + self.b) % PRIME) % self.width
