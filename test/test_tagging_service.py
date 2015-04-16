from random import shuffle

from base import ObjectCubeTestCase
from objectcube.vo import Object, Tagging
from objectcube.exceptions import ObjectCubeException
from objectcube.factory import get_service


class TestTaggingService(ObjectCubeTestCase):

    def __init__(self, *args, **kwargs):
        super(TestTaggingService, self).__init__(*args, **kwargs)
        self.tagging_service = get_service('TaggingService')
        self.object_service = get_service('ObjectService')
        self.tag_service = get_service('TagService')

    def test_add(self):
        db_tag = self.tag_service.add(self._create_test_tag(value='test_tag'))
        db_object = self.object_service.add(Object(name='x', digest='x'))
        db_tagging = self.tagging_service.add(db_object, db_tag, meta=None)
        self.assertEqual(type(db_tagging), Tagging)
        self.assertTrue(db_tagging.id)
        self.assertEqual(db_tagging.object_id, db_object.id)
        self.assertEqual(db_tagging.tag_id, db_tag.id)

        # TODO: verify that it's actually in the data store
