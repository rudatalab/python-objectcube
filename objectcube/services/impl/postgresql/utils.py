import logging
from psycopg2.extras import NamedTupleCursor

from objectcube.contexts import Connection
from objectcube.exceptions import ObjectCubeException
from types import StringTypes, IntType, LongType

StringTypes = StringTypes
IntTypes = (IntType, LongType)

logger = logging.getLogger('db-utils')


def execute_sql_fetch_single(value_object_class, sql, params=()):
    logger.debug('Execute SQL, return single value')
    logger.debug('SQL command: ' + repr(sql) + ' Parameters: ' + repr(params))
    try:
        with Connection() as c:
            with c.cursor(cursor_factory=NamedTupleCursor) as cursor:
                cursor.execute(sql, params)
                row = cursor.fetchone()
                if row:
                    return value_object_class(**row._asdict())
                else:
                    return None
    except Exception as ex:
        logger.error(ex.message)
        raise ObjectCubeException(ex.message)


def execute_sql_fetch_multiple(value_object_class, sql, params):
    logger.debug('Execute SQL, return multiple values')
    logger.debug('SQL command: ' + repr(sql) + ' Parameters: ' + repr(params))
    try:
        with Connection() as c:
            with c.cursor(cursor_factory=NamedTupleCursor) as cursor:
                cursor.execute(sql, params)

                return_list = []
                for row in cursor.fetchall():
                    return_list.append(value_object_class(**row._asdict()))
                return return_list
    except Exception as ex:
        raise ObjectCubeException(ex.message)
