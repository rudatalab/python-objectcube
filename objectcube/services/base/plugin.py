class BasePluginService(object):

    def count(self):
        raise NotImplementedError()

    def get_plugins(self):
        raise NotImplementedError()

    def get_plugin_by_name(self):
        raise NotImplementedError()

    def get_plugin_by_id(self):
        raise NotImplementedError()

    def add_plugin(self, plugin):
        raise NotImplementedError()

    def process(self, _object, _data):
        raise NotImplementedError()