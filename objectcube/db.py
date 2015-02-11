import psycopg2
import settings


def create_connection_string(**kwargs):
    data = {
        'dbname': kwargs.get('dbname', ''),
        'user': kwargs.get('user', ''),
        'host': kwargs.get('host', ''),
        'password': kwargs.get('password', '')
    }
    return ' '.join(['{0}={1}'.format(k, v) for (k, v) in data.items()])


def create_connection():
    db_config = {
        'dbname': settings.DB_DBNAME,
        'user': settings.DB_USER,
        'host': settings.DB_HOST,
        'password': settings.DB_PASSWORD
    }

    try:
        conn = psycopg2.connect(create_connection_string(**db_config))
        return conn
    except Exception:
        raise
