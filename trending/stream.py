def read_stream(path):
    with open(path) as f:
        return [int(line) for line in f]


def exact_counts(stream):
    counts = {}
    for item in stream:
        counts[item] = counts.get(item, 0) + 1
    return counts
