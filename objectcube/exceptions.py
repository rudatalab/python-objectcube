from logging import getLogger
logger = getLogger('DataLayer: Exceptions')


class ObjectCubeException(Exception):
    def __init__(self, *args, **kwargs):
        super(ObjectCubeException, self).__init__(*args, **kwargs)
        logger.debug(repr(self))
