# Trending Now: Finding Heavy Hitters in Massive Data Streams

CSE 4081 Analysis of Algorithms, Fall 2026, Group 11: Roni Asiedu, Orion Powers, Logan Stiller.

The system Trending Now processes a large number of taxi trips in New York City in a single pass without preserving any data for any subsequent processing use. It uses a highly efficient algorithm called Misra-Gries (a Count-Min sketch). The system was developed from scratch and includes an strong counting strategy known as a top-k tracker (the Count-Min sketch plus a small candidate heap), which was tested against an exact counting system.

## Requirements

- Use of Python framework of 3.10 and above with only its inbuilt libraries.
- `pyarrow` is only required by `prepare_data.py`, which is run one time for data reconstruction. It will generate a sample which is already there so there is no more further need of it.

No compilation is needed. Run every command from this folder.

## Layout

| Path | Contents |
| --- | --- |
| `trending/hashing.py` | The universal hash family defined as ((a*x + b) mod p) mod w. |
| `trending/misra_gries.py` | The working of Misra-Gries method using k-1 counters. |
| `trending/count_min.py` | The count-min sketch where the d x w table plus d hashes is utilized. |
| `trending/topk.py` | The top-k tracking, which incorporates count-min sketch and candidate heap. |
| `trending/stream.py` | The stream reader which uses exact counting. |
| `data/pickups.txt` | The data present in the file which consists of 3,000,000 yellow taxi pickup zone ids that are randomly chosen. |
| `prepare_data.py` | The process of downloading the TLC data and constructing the data/pickups.txt. |
| `tests/test_trending.py` | The unit tests. |
| `evaluate.py` | The process of checking accuracy and speed relative to the accurate counts. |
| `demo.py` | The demonstration video includes live trending list and the precise list. |
| `results/results.txt` | Output generated from evaluate.py. |
| `assignment/` | The assignment given to students which consists of description, starting code, input, expected output, and grading scheme. |

## How to run

```
python3 -m unittest discover -s tests -v
python3 evaluate.py > results/results.txt
python3 demo.py
python3 prepare_data.py
```


- `evaluate.py` measures the top-k precision and recall as well as the relative error against Misra-Gries k, sketch width and depth, and k of the tracker. It will take some time to get results.
- `demo.py` takes in `--k`, `--width`, `--depth`, `--events`, `--every`, and `--stream` arguments and then it is able to halve sketch width several times and analyze the points in the stream.
- `prepare_data.py` is used for downloading the TLC yellow-taxi trips for three months (January till March 2024) and keeping the PULocationID of the trips from the stream while generating a random sample of 3,000,000 trips with the seed given.


## Class assignment


The `assignment/` folder contains the assignment record (ASSIGNMENT.md), the starting code which has TODO`s (starter/), the input stream files (inputs/), the output result files expected (expected/), the grading script (grade.py), and the reference solution (solution/).

```
python3 assignment/grade.py assignment/solution
python3 assignment/grade.py assignment/starter
python3 assignment/make_files.py
```

The first command is used for grading the reference solution (10 out of 10), the second one for grading the untouched starter code (0 out of 10) and the third one for regenerating the `inputs/` and `expected/` directories from the file `data/pickups.txt`. The student's submission is graded in exactly the same way by providing the folder with the files misra_gries.py, count_min.py and hashing.py.

## Data

NYC Taxi and Limousine Commission Trip Record Data, yellow taxi trips released by the City of New York in accordance with the NYC's Terms of Use. The TLC did not create the trip data and does not guarantee its accuracy.
https://www1.nyc.gov/site/tlc/about/tlc-trip-record-data.page

## References

- Misra, J., and Gries, D. "Finding repeated elements." Science of Computer Programming 2(2), 143-152, 1982.
- Cormode, G., and Muthukrishnan, S. "An improved data stream summary: the count-min sketch and its applications." Journal of Algorithms 55(1), 58-75, 2005.
- Carter, J. L., and Wegman, M. N. "Universal classes of hash functions." Journal of Computer and System Sciences 18(2), 143-154, 1979.
- NYC Taxi and Limousine Commission. TLC Trip Record Data. City of New York. https://www1.nyc.gov/site/tlc/about/tlc-trip-record-data.page
- CSE 4081 course lectures L08 (Algorithms for Big Data) and L09 (Perfect Hashing).
