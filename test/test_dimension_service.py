from base import TestDatabaseAwareTest
from objectcube.vo import DimensionNode
from objectcube.factory import get_service
from objectcube.exceptions import ObjectCubeException
from objectcube.vo import Tag

class TestDimensionService(TestDatabaseAwareTest):
    def __init__(self, *args, **kwargs):
        super(TestDimensionService, self).__init__(*args, **kwargs)
        self.dimension_service = get_service('DimensionService')

    def test_dimensions_initial_count_zero(self):
        self.assertEquals(self.dimension_service.count(), 0,
                          msg='No dimensions should be in the data store')

    def test_dimensions_add_dimension(self):
        tag = Tag(id=1, value='Test')
        db_node = self.dimension_service.add_dimension(tag)
        self.assertEquals(self.dimension_service.count(), 1,
                          msg='Dimension has not been added')

    def test_dimensions_delete_dimension(self):
        tag = Tag(id=1, value='Test')
        db_node = self.dimension_service.add_dimension(tag)
        self.dimension_service.delete(db_node)
        self.assertEquals(self.dimension_service.count(), 0,
                          msg='Dimension has not been deleted')

