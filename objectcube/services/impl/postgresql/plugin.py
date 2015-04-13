from objectcube.services.base import PluginService
from objectcube.factory import get_service


class PluginServicePostgreSQL(PluginService):

    def count(self):
        pass

    def __init__(self):
        self.tag_service = get_service('tagservice')

    def get_plugin_by_name(self):
        pass

    def add_plugin(self, plugin):
        pass

    def get_plugin_by_id(self):
        pass

    def get_plugins(self):
        pass

    def process(self, _object, _data):
        pass
