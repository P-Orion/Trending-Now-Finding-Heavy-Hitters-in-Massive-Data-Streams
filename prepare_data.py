import os
import random
import tempfile
import time
import urllib.request

import pyarrow.parquet as pq

URL = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{}.parquet"
MONTHS = ["2024-01", "2024-02", "2024-03"]
SAMPLE_SIZE = 3_000_000
SEED = 42
OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "pickups.txt")


def download(url, path, attempts=10):
    for attempt in range(1, attempts + 1):
        try:
            urllib.request.urlretrieve(url, path)
            return
        except OSError as error:
            print("attempt", attempt, "failed:", error)
            time.sleep(2)
    raise RuntimeError("could not download " + url)


def main():
    zones = []
    with tempfile.TemporaryDirectory() as tmp:
        for month in MONTHS:
            path = os.path.join(tmp, month + ".parquet")
            print("downloading", month)
            download(URL.format(month), path)
            column = pq.read_table(path, columns=["PULocationID"]).column(0)
            zones.extend(z for z in column.to_pylist() if z is not None)
    sample = random.Random(SEED).sample(zones, SAMPLE_SIZE)
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "w", newline="\n") as f:
        f.write("\n".join(map(str, sample)))
        f.write("\n")
    print("trips available:", len(zones))
    print("trips sampled:", len(sample))
    print("written to", OUTPUT)


if __name__ == "__main__":
    main()
