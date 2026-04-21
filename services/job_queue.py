from concurrent.futures import ThreadPoolExecutor


class JobQueue:
    def __init__(self, max_workers: int = 1) -> None:
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    def submit(self, fn, *args, **kwargs):
        return self.executor.submit(fn, *args, **kwargs)
