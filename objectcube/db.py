import psycopg2
import settings
from psycopg2.pool import ThreadedConnectionPool


def create_connection_string(**kwargs):
    data = {
        'dbname': kwargs.get('dbname', ''),
        'user': kwargs.get('user', ''),
        'host': kwargs.get('host', ''),
        'password': kwargs.get('password', '')
    }
    return ' '.join(['{0}={1}'.format(k, v) for (k, v) in data.items()])

pool = None


def get_pool():
    global pool
    if not pool:
        db_config = {
            'dbname': settings.DB_DBNAME,
            'user': settings.DB_USER,
            'host': settings.DB_HOST,
            'password': settings.DB_PASSWORD
        }
        minConnections = 1
        maxConnections = 2
        connection_string = create_connection_string(**db_config)
        pool = ThreadedConnectionPool(
            minConnections, maxConnections, connection_string)
    return pool


def create_connection():
    return get_pool().getconn()


def destroy_connection(conn):
    get_pool().putconn(conn)
