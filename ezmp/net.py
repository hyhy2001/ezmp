from typing import Callable, Iterable, List, Any, Optional
from .core import run, run_ordered

def map_urls(
    target_func: Callable,
    urls: Iterable[str],
    ordered: bool = True,
    max_workers: Optional[int] = None,
    desc: str = "Processing URLs"
) -> List[Any]:
    """
    Applies a function to a list of URLs concurrently.
    Always uses threads as network requests are highly I/O bound.
    """
    runner = run_ordered if ordered else run
    return runner(
        target_func=target_func, 
        items=urls, 
        use_threads=True, 
        max_workers=max_workers,
        desc=desc
    )
