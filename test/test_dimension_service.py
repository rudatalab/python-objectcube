from base import TestDatabaseAwareTest
from objectcube.vo import DimensionNode
from objectcube.factory import get_service
from objectcube.exceptions import ObjectCubeException
from objectcube.vo import Tag

class TestDimensionService(TestDatabaseAwareTest):
    def __init__(self, *args, **kwargs):
        super(TestDimensionService, self).__init__(*args, **kwargs)
        self.dimension_service = get_service('DimensionService')

    def test_add_dimension(self):
        tag = Tag(id=1, value='Test')
        db_node = self.dimension_service.add_dimension(tag)

    def test_delete(self):
        tag = Tag(id=1, value='Test')
        db_node = self.dimension_service.add_dimension(tag)
        self.dimension_service.delete(db_node)

