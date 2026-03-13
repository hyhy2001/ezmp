# Project Plan: Easy Multiprocessing (EZMP)

## Overview
The goal is to create a highly accessible, beginner-friendly Python package for multiprocessing. The package will abstract away the complexities of Python's built-in `multiprocessing` and `concurrent.futures` modules. It will focus on common use cases such as processing multiple files, handling data (CSV/Excel), and executing API requests concurrently. All module and function names will be intentionally short and memorable.

## Project Type
BACKEND / LIBRARY

## Success Criteria
- [ ] A new Python beginner can run a multiprocessing task with maximum 3 lines of code.
- [ ] Built-in handlers for common scenarios (Files, API, Dataframes/Excel).
- [ ] Built-in, transparent error logging without crashing the main process by default.
- [ ] Clear performance gain (optimization) over sequential processing.

## Tech Stack
- **Python 3.8+**: Core language.
- **`concurrent.futures`**: The underlying engine for thread/process pools, offering better high-level abstraction natively than `multiprocessing`.
- **`pandas` / `openpyxl`**: Optional dependencies for Excel/CSV specific helpers.
- **`requests`**: Optional dependency for API specific helpers.
- **`tqdm`**: (Removed due to Unix preference)

## File Structure
```text
.
├── ezmp/                  # Main package directory (Short for Easy MultiProcessing)
│   ├── __init__.py        # Exposes main short-named functions
│   ├── core.py            # The main engine/abstractions
│   ├── files.py           # Use case: File processing helpers
│   ├── data.py            # Use case: Excel/CSV processing helpers
│   ├── net.py             # Use case: API/Network processing helpers
│   └── utils.py           # Logging and progress bar utilities
├── tests/                 # Unit tests
├── requirements.txt       # Dependencies
├── setup.py               # Package configuration
└── README.md              # Beginner-friendly documentation
```

## Task Breakdown

### Task 1: Initialize Package and Core Engine
- **Agent**: `backend-specialist`
- **Skills**: `python-patterns`, `clean-code`
- **Priority**: P0
- **Dependencies**: None
- **INPUT**: `ezmp/core.py`, `ezmp/__init__.py`
- **OUTPUT**: A unified `run()` function that accepts an iterable and a target function, automatically spinning up a ProcessPool or ThreadPool based on a simple argument.
- **VERIFY**: Calling `ezmp.run(my_func, my_list)` executes successfully and shows a progress bar.

### Task 2: Implement File Processing Helpers
- **Agent**: `backend-specialist`
- **Skills**: `python-patterns`
- **Priority**: P1
- **Dependencies**: Task 1
- **INPUT**: `ezmp/files.py`
- **OUTPUT**: Functions like `ezmp.files.map_dir(dir_path, my_func)` that automatically get all files in a directory and process them concurrently.
- **VERIFY**: Creating a folder of 10 dummy text files, applying a function to all of them is easily achieved in 2-3 lines of code.

### Task 3: Implement Data (Excel/CSV) Helpers
- **Agent**: `backend-specialist`
- **Skills**: `python-patterns`
- **Priority**: P1
- **Dependencies**: Task 1
- **INPUT**: `ezmp/data.py`
- **OUTPUT**: Functions to split large dataframes/excel files into chunks and process them in parallel.
- **VERIFY**: Processing a mocked 10,000 row CSV file processes row-by-row or chunk-by-chunk significantly faster than sequential.

### Task 4: Error Handling & Logging
- **Agent**: `backend-specialist`
- **Skills**: `clean-code`
- **Priority**: P2
- **Dependencies**: Task 1
- **INPUT**: `ezmp/utils.py`, `ezmp/core.py`
- **OUTPUT**: If a child process raises an Exception, it is caught, logged beautifully to the console, and the return array contains a specific `ErrorResult` object rather than crashing the whole pool.
- **VERIFY**: Purposely throwing an error in one of the tasks logged an error but allowed the remaining tasks to complete.

### Task 5: Documentation & Examples
- **Agent**: `documentation-writer`
- **Skills**: `documentation-templates`
- **Priority**: P3
- **Dependencies**: Tasks 1-4
- **INPUT**: `README.md`, `examples/`
- **OUTPUT**: Highly accessible documentation tailored for absolute beginners.
- **VERIFY**: Readme structure follows best practices and has copy-pasteable examples for 3 main use-cases.

## ✅ Phase X Complete
- Lint: [x] Pass
- Security: [x] No critical issues
- Build: [x] Success
- Date: [2026-03-12]
