class ObjectcubePlugin(object):
    def setup(self):
        raise NotImplementedError()

    def process(self, _object, data):
        raise NotImplementedError()
