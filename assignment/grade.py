import importlib
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from trending.count_min import CountMinSketch as ReferenceCountMin
from trending.misra_gries import MisraGries as ReferenceMisraGries
from trending.stream import read_stream

STREAMS = ["stream_small", "stream_medium", "stream_large"]
MG_K = 50
CMS_WIDTH = 64
CMS_DEPTH = 4
CMS_SEED = 1
SLOWDOWN = 3
SLACK_SECONDS = 1.0


def read_counts(path):
    with open(path) as f:
        return {int(a): int(b) for a, b in (line.split() for line in f)}


def check_misra_gries(summary, counts, n):
    held = summary.heavy_hitters()
    if len(held) > MG_K - 1:
        return False
    for item, f in counts.items():
        if not f - n / MG_K <= summary.estimate(item) <= f:
            return False
        if f > n / MG_K and item not in held:
            return False
    return True


def check_count_min(summary, counts, n):
    epsilon = math.e / CMS_WIDTH
    delta = math.exp(-CMS_DEPTH)
    within = 0
    for item, f in counts.items():
        estimate = summary.estimate(item)
        if estimate < f:
            return False
        if estimate - f <= epsilon * n:
            within += 1
    return within / len(counts) >= 1 - delta


def feed(summary, stream):
    start = time.perf_counter()
    for item in stream:
        summary.update(item)
    return time.perf_counter() - start


def grade(label, make_student, make_reference, check, data):
    attempt = execution = 1
    passed = 0
    student_time = None
    for name, stream, counts in data:
        try:
            summary = make_student()
            elapsed = feed(summary, stream)
            correct = check(summary, counts, len(stream))
        except NotImplementedError as error:
            print(f"{label}: {error}")
            return 0, 0, 0, 0
        except Exception as error:
            print(f"{label}: {name} raised {error!r}")
            execution = 0
            continue
        print(f"{label}: {name} {'correct' if correct else 'WRONG'} ({elapsed:.2f}s)")
        passed += correct
        student_time = elapsed
    if not execution:
        return attempt, 0, 0, 0
    correctness = 2 * passed / len(data)
    efficiency = 0
    if passed == len(data):
        reference_time = feed(make_reference(), data[-1][1])
        limit = SLOWDOWN * reference_time + SLACK_SECONDS
        print(f"{label}: large stream {student_time:.2f}s, limit {limit:.2f}s")
        efficiency = int(student_time <= limit)
    return attempt, execution, correctness, efficiency


def main():
    directory = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(HERE, "starter")
    sys.path.insert(0, directory)
    data = []
    for name in STREAMS:
        stream = read_stream(os.path.join(HERE, "inputs", name + ".txt"))
        counts = read_counts(os.path.join(HERE, "expected", name + ".txt"))
        data.append((name, stream, counts))

    mg_module = importlib.import_module("misra_gries")
    cms_module = importlib.import_module("count_min")
    results = [
        grade(
            "Misra-Gries",
            lambda: mg_module.MisraGries(MG_K),
            lambda: ReferenceMisraGries(MG_K),
            check_misra_gries,
            data,
        ),
        grade(
            "Count-Min",
            lambda: cms_module.CountMinSketch(CMS_WIDTH, CMS_DEPTH, CMS_SEED),
            lambda: ReferenceCountMin(CMS_WIDTH, CMS_DEPTH, CMS_SEED),
            check_count_min,
            data,
        ),
    ]
    total = 0
    for label, (attempt, execution, correctness, efficiency) in zip(("Misra-Gries", "Count-Min"), results):
        points = attempt + execution + correctness + efficiency
        total += points
        print(f"{label}: attempt {attempt}/1, execution {execution}/1, correctness {correctness:.2f}/2, efficiency {efficiency}/1 = {points:.2f}/5")
    print(f"TOTAL: {total:.2f}/10")


if __name__ == "__main__":
    main()
