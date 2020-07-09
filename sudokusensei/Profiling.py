"""quick and dirty way to see how long various things take"""
import functools

import time

def profile(func):
    """Record the runtime of the decorated function"""
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start = time.perf_counter_ns()
        value = func(*args, **kwargs)
        stop = time.perf_counter_ns()
        print(f'{func.__name__} : {(stop - start)/1000_000_000} seconds')
        return value
    return wrapper_timer
