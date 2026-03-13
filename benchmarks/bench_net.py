import time
import ezmp


def mock_io_bound_task(task_id):
    # Simulating a 0.2s network request per item
    time.sleep(0.2)
    return task_id


def run_benchmark():
    items = list(range(100))
    print(
        f"=== I/O Bound Benchmark ({len(items)} Network requests, 0.2s delay each) ==="
    )

    start = time.time()
    for item in items:
        mock_io_bound_task(item)
    seq_time = time.time() - start
    print(f"Sequential 'for' loop: {seq_time:.2f} seconds")

    start = time.time()
    # threads are ideal for IO-bound work
    ezmp.run(mock_io_bound_task, items, use_threads=True, max_workers=50)
    ezmp_time = time.time() - start
    print(f"ezmp.run (Threading):  {ezmp_time:.2f} seconds")

    print(f"Speedup: {(seq_time / ezmp_time):.2f}x\n")


if __name__ == "__main__":
    run_benchmark()
