def catch_error(error_id):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception:
                return {"error": error_id}
        return wrapper
    return decorator

__all__ = ["catch_error"]