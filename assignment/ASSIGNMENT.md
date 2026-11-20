# Assignment: Trending Now - Heavy Hitters in a Data Stream

## Background

A ridesharing app or a taxi fleet produces millions of events (here: one NYC yellow-taxi trip per event, identified by its pickup zone ID). Keeping one counter for every possible item does not scale, and the stream can be read only once. In this assignment you implement two small-memory summaries that find the most frequent items in a single pass.

## What you implement

Complete the TODOs in the two files in `starter/`. Do not rename the classes or methods.

`starter/hashing.py` is given. It is a Carter-Wegman universal hash family: `UniversalHash(width, rng)` is the function `h(x) = ((a*x + b) mod p) mod width`, where `p = 2^61 - 1` and `a`, `b` are drawn from `rng`.

### 1. `misra_gries.py` - `MisraGries(k)`

Keep at most `k - 1` counters in a dictionary. For each item:

1. If the item has a counter, increment it.
2. Otherwise, if fewer than `k - 1` counters exist, create a counter for it with value 1.
3. Otherwise, decrement every counter by 1 and delete the counters that reach 0 (the new item is discarded).

| Method | Behavior |
| --- | --- |
| `update(item)` | process one stream item |
| `estimate(item)` | the counter of `item`, or 0 if it is not tracked |
| `heavy_hitters()` | a dict of every tracked item and its counter |

For a stream of length `n` and true frequency `f` of an item: `f - n/k <= estimate <= f`, and every item with `f > n/k` is tracked.

### 2. `count_min.py` - `CountMinSketch(width, depth, seed)`

Keep a `depth x width` table of counters and `depth` hash functions. Create the rng with `random.Random(seed)`, then build the hash functions one per row with `UniversalHash(width, rng)`.

| Method | Behavior |
| --- | --- |
| `update(item)` | add 1 to `table[row][hash_of_row(item)]` for every row |
| `estimate(item)` | the minimum of `table[row][hash_of_row(item)]` over all rows |

The estimate never undercounts. With `epsilon = e / width` and `delta = e^(-depth)`, the overestimate is at most `epsilon * n` with probability at least `1 - delta`.

## Rules

- Python 3.10 or newer, standard library only. Implement the algorithms yourself; black-box solutions are not allowed.
- Stream items are integers (zone IDs).
- Grading happens on a Unix/Linux machine.

## Files provided

| Path | Contents |
| --- | --- |
| `starter/` | starter code with TODOs (`hashing.py` is complete) |
| `inputs/stream_small.txt`, `stream_medium.txt`, `stream_large.txt` | 10,000 / 100,000 / 1,000,000 events, one zone ID per line |
| `expected/stream_small.txt`, `stream_medium.txt`, `stream_large.txt` | exact counts for the matching input, one `zone count` pair per line, most frequent first |
| `grade.py` | the grading script |
| `solution/` | the reference solution |

`make_files.py` regenerates `inputs/` and `expected/` from `../data/pickups.txt`.

## Running the grader

```
python3 grade.py <directory containing your misra_gries.py, count_min.py and hashing.py>
```

With no argument it grades `starter/`. The grader streams each input file through your classes with `k = 50` for Misra-Gries and `width = 64`, `depth = 4`, `seed = 1` for Count-Min, and compares against the files in `expected/`.

## Grading (10 points)

Each summary is worth 5 points.

| Part | Points per summary | How it is earned |
| --- | --- | --- |
| Attempt | 1 | your code runs without raising `NotImplementedError` |
| Compilation, execution and termination | 1 | your code runs to completion on all three streams without an error |
| Correctness | 2 | split evenly over the three streams, a stream passes when the checks below hold |
| Efficiency | 1 | correct on all streams, and the large stream is processed in at most 3 times the reference solution's time plus 1 second |

Correctness and efficiency are graded only if the program runs and terminates on all inputs.

Misra-Gries checks, for every zone in the expected file: at most `k - 1` counters are held; `f - n/k <= estimate(zone) <= f`; every zone with `f > n/k` is in `heavy_hitters()`.

Count-Min checks, for every zone in the expected file: `estimate(zone) >= f`, and at least a `1 - delta` fraction of zones have `estimate(zone) - f <= epsilon * n`.

## Submission

Submit `misra_gries.py`, `count_min.py` and `hashing.py` through Canvas, along with a note listing your collaborators and any references you used, as described in the syllabus.
