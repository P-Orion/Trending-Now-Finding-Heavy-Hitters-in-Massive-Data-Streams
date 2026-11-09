import argparse

from evaluate import DATA, print_table, tracker_row
from trending.stream import read_stream
from trending.topk import TopK


def show(seen, tracker, counts, k):
    exact = sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))[:k]
    trending = tracker.top()
    print()
    print(f"after {seen:,} events")
    print(f"{'rank':>4}  {'trending zone':>13} {'estimate':>10}   {'exact zone':>10} {'count':>10}")
    for rank in range(k):
        zone, estimate = trending[rank] if rank < len(trending) else ("-", "-")
        exact_zone, exact_count = exact[rank]
        print(f"{rank + 1:>4}  {zone:>13} {estimate:>10}   {exact_zone:>10} {exact_count:>10}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stream", default=DATA)
    parser.add_argument("--k", type=int, default=10)
    parser.add_argument("--width", type=int, default=256)
    parser.add_argument("--depth", type=int, default=5)
    parser.add_argument("--events", type=int, default=1000000)
    parser.add_argument("--every", type=int, default=250000)
    args = parser.parse_args()

    stream = read_stream(args.stream)[: args.events]
    tracker = TopK(args.k, args.width, args.depth, 1)
    counts = {}
    for seen, item in enumerate(stream, 1):
        tracker.update(item)
        counts[item] = counts.get(item, 0) + 1
        if seen % args.every == 0 or seen == len(stream):
            show(seen, tracker, counts, args.k)

    rows = []
    width = args.width
    while width >= 2:
        rows.append((width, tracker_row(stream, counts, args.k, width, args.depth)))
        width //= 2
    print_table(f"Shrinking the sketch (depth {args.depth}, k = {args.k})", "width", rows)


if __name__ == "__main__":
    main()
