import time
import ezmp
import hashlib


def heavy_task(data):
    s = str(data).encode("utf-8")
    for _ in range(1000):
        s = hashlib.md5(s).hexdigest().encode("utf-8")
    return s


def run_benchmark():
    items = list(range(10000))
    print(f"=== CPU Bound Benchmark ({len(items):,} items) ===")

    start = time.time()
    for item in items:
        heavy_task(item)
    seq_time = time.time() - start
    print(f"Sequential 'for' loop: {seq_time:.2f} seconds")

    start = time.time()
    ezmp.run(heavy_task, items)
    ezmp_time = time.time() - start
    print(f"ezmp.run:              {ezmp_time:.2f} seconds")

    print(f"Speedup: {(seq_time / ezmp_time):.2f}x\n")


if __name__ == "__main__":
    run_benchmark()
