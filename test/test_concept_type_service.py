import unittest
from objectcube.db import create_connection
from objectcube import ConceptTypeService
from objectcube.vo import ConceptType
from objectcube.exceptions import (ObjectCubeDatabaseException,
                                   ObjectCubeException)


class TestDatabaseAwareTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestDatabaseAwareTest, self).__init__(*args, **kwargs)

    def setUp(self):
        with open('schema.sql') as fd:
            data = ''.join(fd.readlines())

        with create_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(data)

            connection.commit()


class TestContentTypeService(TestDatabaseAwareTest):

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
        concept_type_service = ConceptTypeService()
        concept_type_name = 'EvenNumbers'
        concept_type_service.add_concept_type(name=concept_type_name)

        with self.assertRaises(ObjectCubeDatabaseException):
            concept_type_service.add_concept_type(name=concept_type_name)

    def test_throws_exception_if_name_is_none(self):
        concept_type_service = ConceptTypeService()

        with self.assertRaises(ObjectCubeDatabaseException):
            concept_type_service.add_concept_type(name=None)

    def test_throws_exception_if_name_is_empty_string(self):
        concept_type_service = ConceptTypeService()

        with self.assertRaises(ObjectCubeDatabaseException):
            concept_type_service.add_concept_type(name=None)

    def test_fetch_by_id_not_found_returns_none(self):
        concept_type_service = ConceptTypeService()
        self.assertIsNone(concept_type_service.get_concept_type_by_id(1000))

    def test_fetch_by_id_single(self):
        concept_type_service = ConceptTypeService()
        data = {
            'name': 'AlphaNumerical',
            'regex_pattern': r'^[a-zA-Z]+[0-9]*[a-zA-Z]*$',
            'concept_base_type': 'REGEX'
        }
        concept_type_service.add_concept_type(**data)

        ct = concept_type_service.get_concept_type_by_id(1)
        self.assertEquals(ct.name, data.get('name'))
        self.assertEquals(ct.regex_pattern, data.get('regex_pattern'))

    def test_fetch_by_id_multiple(self):
        number_of_objects = 50
        concept_type_service = ConceptTypeService()
        for i in range(number_of_objects):
            concept_type_service.add_concept_type(name='test_{}'.format(i+1))

        for i in range(number_of_objects):
            c = concept_type_service.get_concept_type_by_id(i+1)
            self.assertIsNotNone(c)
            self.assertEquals(c.name, 'test_{}'.format(i+1))

    def test_add_concept_type_returns_id(self):
        concept_type_service = ConceptTypeService()
        return_id = concept_type_service.add_concept_type(name='foobar1')
        self.assertEquals(return_id, 1)

        return_id = concept_type_service.add_concept_type(name='foobar2')
        self.assertEquals(return_id, 2)

        self.assertTrue(
            concept_type_service.get_concept_type_by_id(1).name == 'foobar1')
        self.assertTrue(
            concept_type_service.get_concept_type_by_id(2).name == 'foobar2')

    def test_default_base_type(self):
        concept_type_service = ConceptTypeService()
        concept_type_id = concept_type_service.add_concept_type('People')

        c = concept_type_service.get_concept_type_by_id(concept_type_id)

        self.assertEquals(c.concept_base_type,
                          ConceptType.default_type,
                          msg='If not base type for the concept type is '
                              'specified, then the default base type '
                              'defined on the VO should be placed on the '
                              'concept type.')

    def test_create_with_specified_based_type(self):
        concept_type_service = ConceptTypeService()
        concept_type_id = concept_type_service.add_concept_type(
            name='DateTime', concept_base_type='DATETIME')

        concept_type = concept_type_service.get_concept_type_by_id(
            concept_type_id)

        self.assertEquals(concept_type.concept_base_type, 'DATETIME')

    def test_create_with_unknown_based_type_raises_exception(self):
        concept_type_service = ConceptTypeService()
        with self.assertRaises(ObjectCubeException):
            concept_type_service.add_concept_type(name='A',
                                                  concept_base_type='A')

    def test_only_allow_regex_when_REGEX_base_type_is_used(self):
        concept_type_service = ConceptTypeService()

        with self.assertRaises(ObjectCubeException,
                               msg='Regex parameter should only be allowed '
                                   'when we have base type REGEX'):
            concept_type_service.add_concept_type(
                'AlphaNumerical',
                regex_pattern='^[a-zA-Z]+$',
                concept_base_type='ALPHANUMERICAL')