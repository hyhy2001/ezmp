from typing import Callable, Optional, Any, List
from .core import run_ordered # type: ignore

# Add __all__ for explicit exports
__all__ = ["map_df", "map_csv", "map_excel", "map_excel_files", "map_excel_chunks"]

import typing
try:
    import pandas as pd # type: ignore
    DataFrame = pd.DataFrame
except ImportError:
    pd = typing.cast(typing.Any, None)
    DataFrame = typing.Any

def _check_pandas():
    if pd is None:
        raise ImportError(
            "Pandas is required for data helpers. Install ezmp with 'pip install ezmp[data]' "
            "or 'pip install pandas'."
        )

def map_df(
    target_func: Callable,
    df: DataFrame,
    use_threads: bool = False,
    max_workers: Optional[int] = None,
    desc: str = "Processing DataFrame rows"
) -> DataFrame:
    """
    Applies a function to each row of a pandas DataFrame concurrently.
    Because applying heavy transformations is usually CPU bound, defaults to ProcessPool.
    Returns a new DataFrame with a new column 'ezmp_result' containing the return values.
    """
    _check_pandas()
    
    # We pass rows as dictionaries to the target function to make it easy to use
    rows_as_dicts = df.to_dict('records')
    
    # Run concurrently (ordered so we can just append it back as a column)
    results = run_ordered(
        target_func=target_func,
        items=rows_as_dicts,
        use_threads=use_threads,
        max_workers=max_workers,
        desc=desc
    )
    
    # Return a copy of the dataframe with the results appended
    result_df = df.copy()
    result_df['ezmp_result'] = results # type: ignore
    return result_df

def map_csv(
    target_func: Callable,
    file_path: str,
    output_path: Optional[str] = None,
    use_threads: bool = False,
    max_workers: Optional[int] = None,
    desc: str = "Processing CSV rows",
    chunksize: Optional[int] = None,
    **read_csv_kwargs
) -> DataFrame:
    """
    Reads a CSV, processes its rows concurrently, and optionally saves the result.
    If `chunksize` is provided, it returns a generator that yields processed chunk DataFrames.
    This allows massive CSV processing without hitting RAM limits.
    """
    _check_pandas()
    
    if chunksize is not None:
        def chunk_generator():
            for i, chunk in enumerate(pd.read_csv(file_path, chunksize=chunksize, **read_csv_kwargs)):
                yield map_df(
                    target_func=target_func, 
                    df=chunk, 
                    use_threads=use_threads, 
                    max_workers=max_workers, 
                    desc=f"{desc} (chunk {i+1})"
                )
        return chunk_generator()
    else:    
        df = pd.read_csv(file_path, **read_csv_kwargs)
        result_df = map_df(
            target_func=target_func, 
            df=df, 
            use_threads=use_threads, 
            max_workers=max_workers, 
            desc=desc
        )
        
        if output_path is not None:
            result_df.to_csv(output_path, index=False)
            
        return result_df

def map_excel(
    target_func: Callable,
    file_path: str,
    output_path: Optional[str] = None,
    use_threads: bool = False,
    max_workers: Optional[int] = None,
    desc: str = "Processing Excel rows"
) -> DataFrame:
    """
    Reads an Excel file, processes its rows concurrently, and optionally saves the result.
    """
    _check_pandas()
    
    df = pd.read_excel(file_path)
    result_df = map_df(
        target_func=target_func, 
        df=df, 
        use_threads=use_threads, 
        max_workers=max_workers, 
        desc=desc
    )
    
    if output_path is not None:
        result_df.to_excel(output_path, index=False)
        
    return result_df

def _process_single_excel(file_path, target_func, read_kwargs):
    df = pd.read_excel(file_path, **read_kwargs)
    return target_func(df)

def map_excel_chunks(
    target_func: Callable,
    file_path: str,
    chunksize: int = 1000,
    use_threads: bool = False,
    max_workers: Optional[int] = None,
    desc: str = "Processing Excel chunks"
) -> typing.Iterator[DataFrame]:
    """
    Reads an Excel file lazily in chunks, to prevent Out-Of-Memory (OOM) crashes
    on massive SoC matrices (e.g., millions of cells).
    
    Returns a Generator yielding processed DataFrame chunks.
    Dependencies: openpyxl
    """
    _check_pandas()
    import openpyxl # type: ignore
    
    def chunk_generator():
        # Use read_only=True for streaming, drastically reducing memory
        wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
        ws = wb.active
        
        # Get headers
        rows_iter = ws.iter_rows(values_only=True) # type: ignore
        headers = next(rows_iter)
        
        chunk_data = []
        chunk_index = 1
        
        for row in rows_iter:
            chunk_data.append(row)
            if len(chunk_data) >= chunksize:
                # Convert this chunk to a DataFrame
                df_chunk = pd.DataFrame(chunk_data, columns=headers)
                
                # Apply the function concurrently to the rows in this chunk
                processed_df = map_df(
                    target_func=target_func,
                    df=df_chunk,
                    use_threads=use_threads,
                    max_workers=max_workers,
                    desc=f"{desc} (chunk {chunk_index})"
                )
                yield processed_df
                
                chunk_data = []
                chunk_index = chunk_index + 1 # type: ignore
                
        # Process the final remaining chunk if any
        if chunk_data:
            df_chunk = pd.DataFrame(chunk_data, columns=headers)
            yield map_df(
                target_func=target_func,
                df=df_chunk,
                use_threads=use_threads,
                max_workers=max_workers,
                desc=f"{desc} (chunk {chunk_index})"
            )
            
        wb.close()
        
    return chunk_generator()

def map_excel_files(
    target_func: Callable[[DataFrame], Any],
    directory: str,
    recursive: bool = False,
    use_threads: bool = False,
    max_workers: Optional[int] = None,
    desc: str = "Scraping Excel files",
    **read_excel_kwargs
) -> List[Any]:
    """
    Finds all Excel (.xlsx, .xls) files in a directory and applies `target_func`
    to each loaded DataFrame concurrently.
    
    Args:
        target_func: Function to apply to each loaded pd.DataFrame.
        directory: The directory containing Excel files.
        recursive: Whether to search subdirectories.
        use_threads: If True, uses threads; otherwise processes.
        max_workers: Max workers for concurrent execution.
        desc: Progress bar description.
        **read_excel_kwargs: Additional arguments passed to `pd.read_excel`.
        
    Returns:
        A list of results from `target_func`.
    """
    from glob import glob
    import os
    import functools
    
    # Define search pattern
    pattern = "**/*.xls*" if recursive else "*.xls*"
    search_path = os.path.join(directory, pattern)
    
    # Find all excel files
    files = glob(search_path, recursive=recursive)
    
    if not files:
        return []

    wrapper = functools.partial(
        _process_single_excel, 
        target_func=target_func, 
        read_kwargs=read_excel_kwargs
    )

    # Use ezmp core to run concurrently over the files
    from .core import run # type: ignore
    return run(
        target_func=wrapper,
        items=files,
        use_threads=use_threads,
        max_workers=max_workers,
        desc=desc
    )
