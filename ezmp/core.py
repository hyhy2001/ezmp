from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from typing import Callable, Iterable, List, Any, Optional
import multiprocessing

from .utils import log_error # type: ignore

def run(
    target_func: Callable, 
    items: Iterable, 
    use_threads: bool = False, 
    max_workers: Optional[int] = None, 
    desc: str = "Processing"
) -> List[Any]:
    """
    The core engine to easily run a function over an iterable of items.
    
    Args:
        target_func: The function to apply to each item.
        items: An iterable (list, tuple) of items to process.
        use_threads: If True, uses ThreadPoolExecutor (good for I/O bound like API calls). 
                     If False (default), uses ProcessPoolExecutor (good for CPU bound).
        max_workers: The maximum number of workers. Defaults to CPU count for processes.
        desc: Description text for the progress bar.
        
    Returns:
        List of results corresponding to the items. If an error occurs during an item's 
        processing, an ErrorResult is returned in its place rather than crashing.
    """
    
    # Calculate sensible defaults for workers
    if max_workers is None:
        if use_threads:
            # Threads are cheap, default to a high number or min(32, cpu_count + 4)
            max_workers = min(32, (multiprocessing.cpu_count() or 1) + 4)
        else:
            # Processes are heavy, default to CPU count
            max_workers = multiprocessing.cpu_count() or 1

    # Choose Executor
    Executor = ThreadPoolExecutor if use_threads else ProcessPoolExecutor
    
    results = []
    # Using the executor context manager
    with Executor(max_workers=max_workers) as executor:
        # Submit all tasks
        # We store future -> item mapping to know which item failed
        future_to_item = {executor.submit(target_func, item): item for item in items}
        # as_completed yields futures as they finish (regardless of submission order)
        for future in as_completed(future_to_item):
            item = future_to_item[future]
            try:
                res = future.result()
                results.append(res)
            except Exception as exc:
                err_res = log_error(item, exc)
                results.append(err_res)
                    
    # Note: Because as_completed doesn't guarantee order, the results list 
    # will be in the order of completion, not the original items order.
    # We might want to fix this to return ordered results. Let's do that.
    return results

def run_ordered(
    target_func: Callable, 
    items: Iterable, 
    use_threads: bool = False, 
    max_workers: Optional[int] = None, 
    desc: str = "Processing"
) -> List[Any]:
    """
    Like `run()`, but guarantees the returning list is in the exact same 
    order as the input `items`.
    """
    # Convert to list to ensure we can index it and know its length
    items_list = list(items)
    total_items = len(items_list)
    
    if max_workers is None:
        max_workers = min(32, (multiprocessing.cpu_count() or 1) + 4) if use_threads else (multiprocessing.cpu_count() or 1)

    Executor = ThreadPoolExecutor if use_threads else ProcessPoolExecutor
    
    # Pre-allocate results array to keep order
    results = [None] * total_items
    
    with Executor(max_workers=max_workers) as executor:
        # Submit storing the index
        future_to_index = {executor.submit(target_func, item): idx for idx, item in enumerate(items_list)}
        for future in as_completed(future_to_index):
            idx = future_to_index[future]
            item = items_list[idx]
            try:
                res = future.result()
                results[idx] = res
            except Exception as exc:
                err_res = log_error(item, exc)
                results[idx] = err_res
        
    return results

def _unpack_and_call(item_tuple, target_func):
    return target_func(*item_tuple)

def run_multi(
    target_func: Callable, 
    items: Iterable[tuple], 
    use_threads: bool = False, 
    max_workers: Optional[int] = None, 
    desc: str = "Processing multi-args"
) -> List[Any]:
    import functools
    wrapper = functools.partial(_unpack_and_call, target_func=target_func)
    return run(
        target_func=wrapper, # type: ignore
        items=items,
        use_threads=use_threads,
        max_workers=max_workers,
        desc=desc
    )

def run_multi_ordered(
    target_func: Callable, 
    items: Iterable[tuple], 
    use_threads: bool = False, 
    max_workers: Optional[int] = None, 
    desc: str = "Processing multi-args"
) -> List[Any]:
    import functools
    wrapper = functools.partial(_unpack_and_call, target_func=target_func)
    return run_ordered(
        target_func=wrapper, # type: ignore
        items=items,
        use_threads=use_threads,
        max_workers=max_workers,
        desc=desc
    )

