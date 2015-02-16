from objectcube.plugin.base import ObjectcubePlugin


class ExifPlugin(ObjectcubePlugin):
    def setup(self):
        raise NotImplementedError()

    def process(self, _object, data):
        raise NotImplementedError()