from functools import wraps
from db import create_connection


def with_connection(f):
    @wraps(f)
    def dec(*args, **kwargs):
        kwargs['connection'] = create_connection()
        return f(*args, **kwargs)
    return dec
