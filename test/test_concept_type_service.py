from base import TestDatabaseAwareTest
from objectcube import ConceptTypeService
from objectcube.vo import ConceptType
from objectcube.exceptions import (ObjectCubeDatabaseException,
                                   ObjectCubeException)


class TestContentTypeService(TestDatabaseAwareTest):

    def __init__(self, *args, **kwargs):
        super(TestContentTypeService, self).__init__(*args, **kwargs)
        self.concept_type_service = None

    def setUp(self):
        super(TestContentTypeService, self).setUp()
        self.concept_type_service = ConceptTypeService()

    def test_create_new_concept_type(self):
        concept_type_service = ConceptTypeService()

        before_add_number_of_concept_types = \
            concept_type_service.get_concept_type_count()

        concept_type_service.add_concept_type('Odd numbers')
        after_add_number_of_concept_types = \
            concept_type_service.get_concept_type_count()

        self.assertTrue((after_add_number_of_concept_types
                         - before_add_number_of_concept_types) == 1,
                        msg='The distance between the count before and after'
                            'should be one, where adding new type should'
                            'increment the counter by one.')

    def test_uniqueness_of_names(self):
        concept_type_name = 'EvenNumbers'
        self.concept_type_service.add_concept_type(name=concept_type_name)

        with self.assertRaises(ObjectCubeDatabaseException):
            self.concept_type_service.add_concept_type(name=concept_type_name)

    def test_throws_exception_if_name_is_none(self):
        with self.assertRaises(ObjectCubeDatabaseException):
            self.concept_type_service.add_concept_type(name=None)

    def test_throws_exception_if_name_is_empty_string(self):
        with self.assertRaises(ObjectCubeDatabaseException):
            self.concept_type_service.add_concept_type(name=None)

    def test_fetch_by_id_not_found_returns_none(self):
        self.assertIsNone(
            self.concept_type_service.get_concept_type_by_id(1000))

    def test_fetch_by_id_single(self):
        data = {
            'name': 'AlphaNumerical',
            'regex_pattern': r'^[a-zA-Z]+[0-9]*[a-zA-Z]*$',
            'concept_base_type': 'REGEX'
        }
        self.concept_type_service.add_concept_type(**data)

        ct = self.concept_type_service.get_concept_type_by_id(1)
        self.assertEquals(ct.name, data.get('name'))
        self.assertEquals(ct.regex_pattern, data.get('regex_pattern'))

    def test_fetch_by_id_multiple(self):
        number_of_objects = 50
        for i in range(number_of_objects):
            self.concept_type_service.add_concept_type(
                name='test_{}'.format(i+1))

        for i in range(number_of_objects):
            c = self.concept_type_service.get_concept_type_by_id(i+1)
            self.assertIsNotNone(c)
            self.assertEquals(c.name, 'test_{}'.format(i+1))

    def test_add_concept_type_concept_type_object_with_data(self):
        c1 = self.concept_type_service.add_concept_type(name='foobar1')
        self.assertEquals(c1.__class__, ConceptType)
        self.assertEquals(c1.name, 'foobar1')

    def test_default_base_type(self):
        c = self.concept_type_service.add_concept_type('People')

        self.assertEquals(c.concept_base_type,
                          ConceptType.default_type,
                          msg='If not base type for the concept type is '
                              'specified, then the default base type '
                              'defined on the VO should be placed on the '
                              'concept type.')

    def test_create_with_specified_based_type(self):
        concept_type = self.concept_type_service.add_concept_type(
            name='DateTime', concept_base_type='DATETIME')
        self.assertEquals(concept_type.concept_base_type, 'DATETIME')

    def test_create_with_unknown_based_type_raises_exception(self):
        with self.assertRaises(ObjectCubeException):
            self.concept_type_service.add_concept_type(name='A',
                                                  concept_base_type='A')

    def test_only_allow_regex_when_REGEX_base_type_is_used(self):

        with self.assertRaises(ObjectCubeException,
                               msg='Regex parameter should only be allowed '
                                   'when we have base type REGEX'):
            self.concept_type_service.add_concept_type(
                'AlphaNumerical',
                regex_pattern='^[a-zA-Z]+$',
                concept_base_type='ALPHANUMERICAL')