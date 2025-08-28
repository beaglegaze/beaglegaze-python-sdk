import functools

def usage_logger(func):
    """
    Decorator that logs the call of a method.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"[Call tracked]: {func.__module__}.{func.__name__}")
        return func(*args, **kwargs)
    return wrapper
