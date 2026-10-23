import math
import os
import random
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trending.count_min import CountMinSketch
from trending.hashing import PRIME, UniversalHash
from trending.misra_gries import MisraGries
from trending.stream import exact_counts
from trending.topk import TopK


def skewed_stream(n, universe, seed):
    rng = random.Random(seed)
    weights = [1 / (i + 1) for i in range(universe)]
    return rng.choices(range(1, universe + 1), weights=weights, k=n)


class HashTests(unittest.TestCase):
    def test_range(self):
        rng = random.Random(1)
        for width in (1, 7, 64, 265):
            h = UniversalHash(width, rng)
            for x in range(1, 1000):
                self.assertTrue(0 <= h(x) < width)

    def test_parameters_in_bounds(self):
        rng = random.Random(2)
        for _ in range(100):
            h = UniversalHash(10, rng)
            self.assertTrue(1 <= h.a < PRIME)
            self.assertTrue(0 <= h.b < PRIME)

    def test_same_seed_same_function(self):
        h1 = UniversalHash(50, random.Random(3))
        h2 = UniversalHash(50, random.Random(3))
        self.assertEqual([h1(x) for x in range(100)], [h2(x) for x in range(100)])

    def test_collision_rate_close_to_one_over_width(self):
        width = 64
        rng = random.Random(4)
        pairs = [(x, y) for x in range(1, 41) for y in range(x + 1, 41)]
        collisions = 0
        trials = 200
        for _ in range(trials):
            h = UniversalHash(width, rng)
            collisions += sum(1 for x, y in pairs if h(x) == h(y))
        rate = collisions / (trials * len(pairs))
        self.assertLess(rate, 2 / width)


class MisraGriesTests(unittest.TestCase):
    def test_small_example(self):
        mg = MisraGries(3)
        for item in [1, 1, 2, 3, 1]:
            mg.update(item)
        self.assertEqual(mg.heavy_hitters(), {1: 2})

    def test_counter_limit(self):
        for k in (2, 5, 20):
            mg = MisraGries(k)
            for item in skewed_stream(5000, 100, k):
                mg.update(item)
                self.assertLessEqual(len(mg.heavy_hitters()), k - 1)

    def test_guarantees(self):
        for k in (5, 10, 25, 60):
            stream = skewed_stream(20000, 150, k)
            n = len(stream)
            counts = exact_counts(stream)
            mg = MisraGries(k)
            for item in stream:
                mg.update(item)
            for item, f in counts.items():
                est = mg.estimate(item)
                self.assertLessEqual(est, f)
                self.assertGreaterEqual(est, f - n / k)
                if f > n / k:
                    self.assertIn(item, mg.heavy_hitters())


class CountMinTests(unittest.TestCase):
    def test_never_undercounts(self):
        stream = skewed_stream(20000, 200, 5)
        counts = exact_counts(stream)
        cms = CountMinSketch(16, 3, seed=1)
        for item in stream:
            cms.update(item)
        for item, f in counts.items():
            self.assertGreaterEqual(cms.estimate(item), f)

    def test_error_bound(self):
        stream = skewed_stream(20000, 200, 6)
        n = len(stream)
        counts = exact_counts(stream)
        epsilon, delta = 0.05, 0.01
        width = math.ceil(math.e / epsilon)
        depth = math.ceil(math.log(1 / delta))
        cms = CountMinSketch(width, depth, seed=2)
        for item in stream:
            cms.update(item)
        within = sum(1 for item, f in counts.items() if cms.estimate(item) - f <= epsilon * n)
        self.assertGreaterEqual(within / len(counts), 1 - delta)

    def test_exact_when_wide(self):
        cms = CountMinSketch(100000, 4, seed=3)
        for item in [1, 2, 2, 3, 3, 3]:
            cms.update(item)
        self.assertEqual([cms.estimate(i) for i in (1, 2, 3, 4)], [1, 2, 3, 0])

    def test_shape(self):
        cms = CountMinSketch(10, 4)
        self.assertEqual(len(cms.table), 4)
        self.assertTrue(all(len(row) == 10 for row in cms.table))
        self.assertEqual(len(cms.hashes), 4)


class TopKTests(unittest.TestCase):
    def test_finds_true_top_k(self):
        stream = skewed_stream(30000, 200, 7)
        counts = exact_counts(stream)
        k = 10
        tracker = TopK(k, 256, 5, seed=1)
        for item in stream:
            tracker.update(item)
        reported = {item for item, _ in tracker.top()}
        exact = {item for item, _ in sorted(counts.items(), key=lambda p: (-p[1], p[0]))[:k]}
        self.assertEqual(reported, exact)

    def test_candidate_limit_and_order(self):
        stream = skewed_stream(10000, 100, 8)
        tracker = TopK(5, 32, 3, seed=2)
        for item in stream:
            tracker.update(item)
            self.assertLessEqual(len(tracker.candidates), 5)
            self.assertLessEqual(len(tracker.heap), 5)
        estimates = [est for _, est in tracker.top()]
        self.assertEqual(estimates, sorted(estimates, reverse=True))

    def test_estimates_never_below_true_count(self):
        stream = skewed_stream(10000, 100, 9)
        counts = exact_counts(stream)
        tracker = TopK(8, 32, 3, seed=3)
        for item in stream:
            tracker.update(item)
        for item, est in tracker.top():
            self.assertGreaterEqual(est, counts[item])


if __name__ == "__main__":
    unittest.main()
