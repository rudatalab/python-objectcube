from db import create_connection, destroy_connection


class Connection:
    def __init__(self):
        self.connection = None

    def __enter__(self):
        self.connection = create_connection()
        return self.connection

    def __exit__(self, *args, **kwargs):
        try:
            self.connection.commit()
        except Exception:
            raise
        finally:
            destroy_connection(self.connection)

    def cursor(self, *args, **kwargs):
        return self.connection.cursor(*args, **kwargs)
