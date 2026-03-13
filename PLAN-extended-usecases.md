# Project Plan: EZMP Extended Use-Cases

## Overview
Building upon the success of the core engine, we will expand `ezmp` to handle heavier, real-world data tasks:
1. **Multi-Input Task (`ezmp.run_multi` & `ezmp.run_multi_ordered`)**: Support passing multiple arguments (`*args` and `**kwargs`) easily to target functions using Tuples.
2. **Parsing Huge Logs (`ezmp.logs`)**: Handle massive text/log files (GBs in size) by reading data in chunks using Python Generators, allowing parallel processing without crashing RAM.
3. **Excel File Scraping (`ezmp.data.map_excel_files`)**: Concurrently read and process a large number of Excel files scattered in a directory.
4. **Processing Composition (Lazy Generators)**: Ensure all read functions return Generators. The user has full control to write custom `if/else` logic in between the reading and processing phases, grabbing only the filtered data they need, and passing it into `ezmp.run()`.

## Project Type
BACKEND / LIBRARY

## Success Criteria
- [ ] `run_multi` functions allow passing lists of tuples easily (unpacking arguments mapped to the target function).
- [ ] `ezmp` can read a massive file in chunks via an iterator yielding data, occupying minimal memory footprint.
- [ ] Mass directory scanning and Excel reading mapped concurrently to a target function.
- [ ] All code, comments, variables, and examples MUST be written in English.

## Tech Stack
- **Python 3.8+**
- **`pandas` / `openpyxl`**: For Excel handling.
- **Python Generators**: Streaming data architecture to prevent memory overhead during composition pipelines.
- Improvise Core Engine (`core.py`) with `starmap` patterns.

## File Structure
```text
.
├── ezmp/                  
│   ├── __init__.py        
│   ├── core.py            # [MODIFY] Add run_multi, run_multi_ordered
│   ├── files.py           
│   ├── logs.py            # [NEW] Handle big files, stream chunk readers 
│   ├── data.py            # [MODIFY] Add map_excel_directory
│   ...
```

## Task Breakdown

### Task 1: Support Multi-Args Processing (run_multi)
- **Agent**: `backend-specialist`
- **Skills**: `python-patterns`, `clean-code`
- **Priority**: P0
- **Dependencies**: None
- **INPUT**: `ezmp/core.py`, `ezmp/__init__.py`
- **OUTPUT**: Implementation of `run_multi` and `run_multi_ordered` accepting an iterable of tuples, which automatically unpacks into the arguments of `target_func`.
- **VERIFY**: Passing `[(1, 2), (3, 4)]` into `def add(x, y)` executes correctly without manual unpacking lambda hacks.

### Task 2: Huge Log Parsing Module (Generators)
- **Agent**: `backend-specialist`
- **Skills**: `python-patterns`
- **Priority**: P1
- **Dependencies**: Task 1
- **INPUT**: `ezmp/logs.py`
- **OUTPUT**: `ezmp.logs.read_chunks` function returning a Generator that yields batches of N lines from a massive text file. 
- **VERIFY**: Reading a dummy 1GB file occupies less than 50MB RAM during the parsing/filtering phase.

### Task 3: Mass Excel Scraping 
- **Agent**: `backend-specialist`
- **Skills**: `python-patterns`
- **Priority**: P1
- **Dependencies**: Task 1
- **INPUT**: `ezmp/data.py`
- **OUTPUT**: `ezmp.data.map_excel_files(target_func, directory)` quickly glob-searches for `.xlsx` files and reads them concurrently using threads/processes.
- **VERIFY**: Extracting "Cell A1" from 20 dummy Excel files completes rapidly via concurrent futures.

### Task 4: Modularity and Composition (User Logic)
- **Agent**: `backend-specialist`
- **Skills**: `python-patterns`, `clean-code`
- **Priority**: P1
- **Dependencies**: Task 1, 2, 3
- **INPUT**: `ezmp/logs.py`, `ezmp/data.py`
- **OUTPUT**: Ensuring read operations yield iterables. Users can take the generator, run their own native Python loops to extract needed data, and pass the clean data to output functions.
- **VERIFY**: Write an example where User gets chunks from Log A -> User uses `if` block for picking "ERROR" lines -> User passes the filtered lines to `ezmp.run()`. User retains full control between steps.

### Task 5: Documentation & Testing for New Features
- **Agent**: `documentation-writer`
- **Skills**: `documentation-templates`
- **Priority**: P2
- **Dependencies**: Task 1, 2, 3, 4
- **INPUT**: `README.md`, `tests/test_ezmp_extended.py`
- **OUTPUT**: Write Tests mapped to features. Update `README.md` in English detailing "Scraping 100 Excel files" and "Streaming Huge Logs with Composition".
- **VERIFY**: 100% Tests passing, beginner friendly documentation.

## ✅ Phase X Complete
- Lint: [x] Pass
- Security: [x] No critical issues
- Build: [x] Success
- Date: [2026-03-13]
