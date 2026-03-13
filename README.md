# Easy Multiprocessing (ezmp)

`ezmp` is a beginner-friendly Python package that makes concurrent execution (multiprocessing and multithreading) incredibly simple. It removes the boilerplate associated with `concurrent.futures`, and adds safe error handling so that a single failing item doesn't crash your entire script.

**Recently updated for EDA workflows:** Effortlessly parse gigabyte-sized Static Timing Analysis (STA) reports and stream massive SoC boolean matrices without crashing your system's RAM.

---

## 🚀 Features

- **Zero Boilerplate**: Run CPU-heavy tasks or Network I/O tasks instantly.
- **Ordered/Unordered**: Choose between strict order preservation or maximum speed.
- **Multi-arguments**: Pass tuples of arguments seamlessly (`run_multi`), avoiding lambda wrappers.
- **Massive File Chunking (No OOM)**: Stream gigabyte-sized Log files or Excel Matrices into manageable chunks.
- **Custom Block Extraction**: Inject your own Python parsing logic into log readers to extract multi-line blocks dynamically.
- **Stream Output**: Pipe results directly to output files line-by-line using generators (`write_stream`).
- **Robust Error Handling**: Wraps exceptions in `ErrorResult` instead of crashing the pool.

---

## 📦 Installation

Install the base package:
```bash
pip install ezmp
```

**Optional Dependencies:**
If you want to use the `data` (Excel/CSV) or `net` modules, you can install the optional dependencies:
```bash
pip install "ezmp[data]"  # Installs pandas, openpyxl
pip install "ezmp[net]"   # Installs requests
pip install "ezmp[all]"   # Installs everything
```

---

## 📖 Quickstart Examples

### 1. Basic Multiprocessing (CPU Bound)
The simplest way to use `ezmp`. By default, it uses Python processes to max out your CPU cores.

```python
import ezmp
import time

def heavy_computation(x):
    time.sleep(1) # simulate work
    return x * x

items = [1, 2, 3, 4, 5, 6, 7, 8]
# Returns quickly!
results = ezmp.run(heavy_computation, items)
print(results)
```

### 2. Multi-Arguments
If your target function expects multiple arguments, pass them as tuples using `run_multi`.

```python
import ezmp

def add_coordinates(x, y):
    return x + y

points = [(1, 2), (10, 20), (5, 5)]

# Unpacks the tuples automatically
results = ezmp.run_multi(add_coordinates, points)
print(results)  # [3, 30, 10]
```

### 3. Extracting Multi-line Blocks from Huge Logs
STA Path logs often have multi-line blocks. Use `parse_blocks` to stream the file and use a custom Python function to extract the exact blocks you need.

```python
import ezmp

# 1. Define your custom multi-line block extractor
def sta_extractor(chunk, state):
    if not state:
        state.update({'in_path': False, 'current_start': None})
        
    for line in chunk:
        if line.startswith("Startpoint:"):
            state['in_path'] = True
            state['current_start'] = line.split()[1]
        elif line.startswith("slack (VIOLATED)") and state['in_path']:
            yield {'start': state['current_start'], 'slack': float(line.split()[-1])}
            state['in_path'] = False

# 2. Get a lazy generator that parses a massive log file without eating RAM
generator = ezmp.logs.parse_blocks("massive_sta.rpt", sta_extractor)

# 3. Stream the results straight to a file
def to_csv(item):
    return f"{item['start']},{item['slack']}"

ezmp.files.write_stream(generator, "violations.csv", transform=to_csv)
```

### 4. Streaming Enormous Excel Matrices
Pandas `read_excel` will crash on wide boolean matrices. Use `map_excel_chunks` to stream them lazily.

```python
import ezmp

def count_active_clocks(df_chunk):
    # Sum across columns (True=1, False=0)
    return df_chunk.sum(axis=1)

# Stream 2,000 rows at a time, processed concurrently
generator = ezmp.data.map_excel_chunks(count_active_clocks, "huge_soc_matrix.xlsx", chunksize=2000)

for processed_chunk_df in generator:
    print(processed_chunk_df['ezmp_result'])
```

### 5. Nested Execution (Auto-Fallback)
Running multiprocessing pools inside other multiprocessing pools causes severe bugs (like `daemonic processes are not allowed to have children` or thread pool deadlocks). `ezmp` detects these nested calls automatically and gracefully downshifts the inner function to sequential execution, shielding you from crashes.

```python
import ezmp
import time

def process_file(x):
    time.sleep(0.1)
    return x * 10

def process_folder(folder_contents):
    # This nested call is perfectly safe. 
    # ezmp automatically falls back to sequential execution.
    return ezmp.run(process_file, folder_contents)

folders = [[1, 2], [3, 4], [5, 6]]

# Only the outer layer spins up a multiprocessing pool
ezmp.run(process_folder, folders)
```

### 6. Parallel Processing Multiple Massive Excel Files (Pro Pattern)
If you have **100s of massive Excel matrices** (e.g., 100 Million cells each), attempting to load them all into RAM concurrently using `pd.read_excel` will destroy your system (OOM). 

Instead, harness the power of `ezmp`'s Auto-Fallback feature by nesting a chunked reader inside a parallel directory scanner:

```python
import ezmp

# 1. Row processor (Runs Sequentially on each chunk row inside the file worker)
def count_true_clocks(row_dict):
    return sum(1 for val in row_dict.values() if val is True)

# 2. File processor (The parent target function)
def process_massive_file(file_path):
    # This automatically detects it is inside a Worker Process!
    # Instead of spawning more processes, it safely iterates the file via a Generator.
    chunks_gen = ezmp.excel.map_excel_chunks(
        count_true_clocks, 
        file_path, 
        chunksize=1000 # Memory stays tiny (e.g 1000 rows limit)
    )
    
    # Aggregate chunk results
    total = sum(chunk_df['ezmp_result'].sum() for chunk_df in chunks_gen)
    return total

# 3. Process the entire directory of massive files concurrently!
results = ezmp.files.map_dir(
    target_func=process_massive_file,
    dir_path="/path/to/massive/matrices/",
    pattern="*.xlsx",
    max_workers=8 # Spawns 8 Concurrent Processes parsing 8 files stream-wise
)
```

---

## 🛠️ API Reference

### `ezmp.core`
- `run(func, items, use_threads=False, max_workers=None)`: Core map. CPU bound by default.
- `run_ordered(...)`: Same as `run`, but guarantees order.
- `run_stream(func, items, ...)`: Returns a lazy-evaluated Generator. Yields results one-by-one as they complete. Ideal for saving RAM.
- `run_multi(func, items_tuples)`: Accepts an iterable of tuples and unpacks them `func(*item)`.
- `run_multi_ordered(...)`: Same as multi, but strict order.

### `ezmp.files`
- `map_files(func, file_list, use_threads=True)`
- `map_dir(func, directory, pattern, ...)`
- `write_stream(results_generator, output_path, transform=None)`: Safely writes generated items to a file sequentially.

### `ezmp.dataframe`
- `map_df(func, df)`: Process a DataFrame row-by-row concurrently.

### `ezmp.csv`
- `map_csv(func, file_path, chunksize=None)`: Specify `chunksize` to return a Generator for low-RAM streaming.

### `ezmp.excel`
- `map_excel(...)`: Read & process single Excel file (High RAM usage).
- `map_excel_files(func, directory)`: Process all excel files concurrently.
- `map_excel_chunks(func, file_path, chunksize=1000)`: Read a massive Excel file lazily and process chunk-by-chunk (Low RAM footprint).

### `ezmp.net`
- `map_urls(func, urls)`: Downloads/processes URLs using threads.

### `ezmp.logs`
- `read_chunks(file_path, chunk_size=1000)`: Yields raw lists of text lines.
- `parse_blocks(file_path, block_extractor, chunk_size)`: Feeds text lines to your custom `block_extractor` function for complex stateful parsing.
