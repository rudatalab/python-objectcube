import logging

logger = logging.getLogger('db-exceptions')

class ObjectCubeException(Exception):
    def __init__(self, *args, **kwargs):
        super(ObjectCubeException, self).__init__(*args, **kwargs)
        logger.debug(repr(self))


