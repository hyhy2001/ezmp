import time
import ezmp
import pandas as pd
import numpy as np


def compute_heavy_score(row_dict):
    # Simulate a heavy math computation per row
    val = (row_dict["A"] * row_dict["B"]) / (row_dict["C"] + 0.0001)
    val += len(str(row_dict["D"]))
    return val


def run_benchmark():
    n_rows = 5000
    df = pd.DataFrame(
        {
            "A": np.random.rand(n_rows),
            "B": np.random.rand(n_rows),
            "C": np.random.rand(n_rows),
            "D": ["item_" + str(i) for i in range(n_rows)],
        }
    )

    print(f"=== Pandas DataFrame Benchmark ({n_rows:,} rows) ===")

    # Sequential
    start = time.time()
    _ = df.apply(compute_heavy_score, axis=1)
    seq_time = time.time() - start
    print(f"df.apply(axis=1):      {seq_time:.2f} seconds")

    # ezmp parallel
    start = time.time()
    _ = ezmp.dataframe.map_df(compute_heavy_score, df)
    ezmp_time = time.time() - start
    print(f"ezmp.dataframe.map_df: {ezmp_time:.2f} seconds")

    print(f"Speedup: {(seq_time / ezmp_time):.2f}x\n")


if __name__ == "__main__":
    run_benchmark()
