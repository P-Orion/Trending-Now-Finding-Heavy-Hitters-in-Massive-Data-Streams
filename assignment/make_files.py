import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from trending.stream import exact_counts, read_stream

SOURCE = os.path.join(ROOT, "data", "pickups.txt")
SIZES = {"stream_small": 10000, "stream_medium": 100000, "stream_large": 1000000}


def main():
    stream = read_stream(SOURCE)
    os.makedirs(os.path.join(HERE, "inputs"), exist_ok=True)
    os.makedirs(os.path.join(HERE, "expected"), exist_ok=True)
    for name, size in SIZES.items():
        part = stream[:size]
        with open(os.path.join(HERE, "inputs", name + ".txt"), "w", newline="\n") as f:
            f.write("\n".join(map(str, part)) + "\n")
        ranked = sorted(exact_counts(part).items(), key=lambda pair: (-pair[1], pair[0]))
        with open(os.path.join(HERE, "expected", name + ".txt"), "w", newline="\n") as f:
            for item, count in ranked:
                f.write(f"{item} {count}\n")


if __name__ == "__main__":
    main()
