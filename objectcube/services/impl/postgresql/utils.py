import logging
from psycopg2.extras import NamedTupleCursor

from objectcube.contexts import Connection
from objectcube.exceptions import ObjectCubeDatabaseException

logger = logging.getLogger('db-utils')


def execute_single_sql(value_object_class, sql, params=(), commit=True):
    try:
        with Connection() as c:
            with c.cursor(cursor_factory=NamedTupleCursor) as cursor:
                cursor.execute(sql, params)
                row = cursor.fetchone()
                if commit:
                    c.commit()
                if row:
                    return value_object_class(**row._asdict())
    except Exception as ex:
        logger.error(ex.message)
        raise ObjectCubeDatabaseException(ex)


def retrieve_multiple_tags(value_object_class, sql, params):
    try:
        with Connection() as c:
            with c.cursor(cursor_factory=NamedTupleCursor) as cursor:
                cursor.execute(sql, params)

                return_list = []
                for row in cursor.fetchall():
                    return_list.append(value_object_class(**row._asdict()))
                return return_list
    except Exception as e:
        raise ObjectCubeDatabaseException(e)
