from multiprocessing import Manager
from typing import Any, Optional


class GlobalCache:
    """
    A multiprocess-safe caching layer specifically designed to store heavy,
    frequently accessed Excel Data Ranges (like 'Sheet2!A1:Z10000').
    Since hundreds of parallel workers might execute VLOOKUP on the exact same referencing table,
    extracting that table using openpyxl hundreds of times would cripple performance.

    The first worker to evaluate the range extracts it, then publishes it here.
    Remaining workers cleanly deserialize it via IPC O(1) latency.
    """

    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self._manager = None
        self._cache = None

        if self.enabled:
            # Shared Multiprocessing dictionary proxy
            self._manager = Manager()
            self._cache = self._manager.dict()

    def get(self, key: str) -> Optional[Any]:
        if not self.enabled or self._cache is None:
            return None
        return self._cache.get(key)

    def set(self, key: str, value: Any):
        if self.enabled and self._cache is not None:
            self._cache[key] = value

    def shutdown(self):
        if self._manager:
            self._manager.shutdown()
