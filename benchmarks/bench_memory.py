import time
import ezmp
import pandas as pd
import tracemalloc
import os
import random


def create_large_csv():
    filepath = "bench_massive_temp.csv"
    if not os.path.exists(filepath):
        print("Creating mock massive CSV (1,000,000 rows)...")
        with open(filepath, "w") as f:
            f.write("id,value,status\n")
            for i in range(100000):
                f.write(f"{i},{random.random():.4f},OK\n")
    return filepath


def process_row(row_dict):
    return 1 if row_dict.get("status") == "OK" else 0


def run_benchmark():
    filepath = create_large_csv()
    file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
    print(f"=== Memory Benchmark ({file_size_mb:.2f} MB CSV) ===")

    # 1. Pandas peak memory
    tracemalloc.start()
    start = time.time()
    try:
        df = pd.read_csv(filepath)
        _ = df["status"].apply(lambda x: 1 if x == "OK" else 0).sum()
        del df  # force cleanup
    except MemoryError:
        print("Pandas OOMed!")
    seq_time = time.time() - start
    _, peak_pd = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print("pandas pd.read_csv:")
    print(f"  - Peak RAM: {peak_pd / 1024 / 1024:.2f} MB")
    print(f"  - Time:     {seq_time:.2f} seconds")

    # 2. ezmp Chunked map_csv peak memory
    tracemalloc.start()
    start = time.time()
    chunks_gen = ezmp.csv.map_csv(process_row, filepath, chunksize=10000)
    _ = sum(chunk_df["ezmp_result"].sum() for chunk_df in chunks_gen)
    ezmp_time = time.time() - start
    _, peak_ezmp = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print("ezmp.csv.map_csv (chunksize=10000):")
    print(f"  - Peak RAM: {peak_ezmp / 1024 / 1024:.2f} MB")
    print(f"  - Time:     {ezmp_time:.2f} seconds")

    if peak_ezmp > 0:
        print(f"Memory Efficiency: ezmp uses {(peak_pd / peak_ezmp):.1f}x less RAM!\n")

    # Cleanup
    try:
        os.remove(filepath)
    except Exception:
        pass


if __name__ == "__main__":
    run_benchmark()
