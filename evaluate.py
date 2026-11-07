import os
import sys
import time

from trending.count_min import CountMinSketch
from trending.misra_gries import MisraGries
from trending.stream import exact_counts, read_stream
from trending.topk import TopK

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "pickups.txt")
SEED = 1
K = 10


def exact_top(counts, k):
    ranked = sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))
    return [item for item, _ in ranked[:k]]


def precision_recall(reported, exact, k):
    hits = len(set(reported) & set(exact))
    precision = hits / len(reported) if reported else 0.0
    return precision, hits / k


def relative_error(estimate, counts, items):
    return sum(abs(estimate(i) - counts[i]) / counts[i] for i in items) / len(items)


def run(summary, stream):
    for item in stream:
        summary.update(item)
    return summary


def mg_row(stream, counts, m):
    mg = run(MisraGries(m), stream)
    exact = exact_top(counts, K)
    ranked = sorted(mg.heavy_hitters().items(), key=lambda pair: (-pair[1], pair[0]))
    reported = [item for item, _ in ranked[:K]]
    precision, recall = precision_recall(reported, exact, K)
    error = relative_error(mg.estimate, counts, exact)
    return m - 1, precision, recall, error


def tracker_row(stream, counts, k, width, depth):
    tracker = run(TopK(k, width, depth, SEED), stream)
    exact = exact_top(counts, k)
    reported = [item for item, _ in tracker.top()]
    precision, recall = precision_recall(reported, exact, k)
    error = relative_error(tracker.sketch.estimate, counts, exact)
    return depth * width + k, precision, recall, error


def print_table(title, first, rows):
    print()
    print(title)
    print(f"{first:>10} {'counters':>9} {'precision':>10} {'recall':>8} {'rel.error':>10}")
    for label, (counters, precision, recall, error) in rows:
        print(f"{label:>10} {counters:>9} {precision:>10.2f} {recall:>8.2f} {error:>10.4f}")


def events_per_second(update, stream):
    start = time.perf_counter()
    for item in stream:
        update(item)
    return len(stream) / (time.perf_counter() - start)


def speed_table(stream):
    counts = {}

    def count(item):
        counts[item] = counts.get(item, 0) + 1

    contenders = [
        ("exact dict counter", count),
        ("Misra-Gries (k=50)", MisraGries(50).update),
        ("Count-Min (64 x 5)", CountMinSketch(64, 5, SEED).update),
        ("Top-k tracker (k=10, 64 x 5)", TopK(10, 64, 5, SEED).update),
    ]
    print()
    print("Speed (single pass over the whole stream)")
    print(f"{'method':<30} {'events/sec':>12}")
    for name, update in contenders:
        print(f"{name:<30} {events_per_second(update, stream):>12,.0f}")


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else DATA
    stream = read_stream(path)
    counts = exact_counts(stream)
    print("stream:", path)
    print("events n:", len(stream))
    print("distinct zones:", len(counts))
    print("top-k size K for tables 1-3:", K)
    print("exact top-K:", exact_top(counts, K))

    print_table(
        "Table 1: Misra-Gries, accuracy vs k (top-K, k-1 counters)",
        "k",
        [(m, mg_row(stream, counts, m)) for m in (10, 20, 50, 100, 200, 300)],
    )
    print_table(
        "Table 2: top-k tracker, accuracy vs sketch width (depth 5, k = 10)",
        "width",
        [(w, tracker_row(stream, counts, K, w, 5)) for w in (4, 8, 16, 32, 64, 128, 256)],
    )
    print_table(
        "Table 3: top-k tracker, accuracy vs sketch depth (width 32, k = 10)",
        "depth",
        [(d, tracker_row(stream, counts, K, 32, d)) for d in (1, 2, 3, 4, 5, 8)],
    )
    print_table(
        "Table 4: top-k tracker, accuracy vs k (width 64, depth 5)",
        "k",
        [(k, tracker_row(stream, counts, k, 64, 5)) for k in (5, 10, 20, 50)],
    )
    speed_table(stream)


if __name__ == "__main__":
    main()
