from base import TestDatabaseAwareTest
from objectcube.services.concept import ConceptService
from objectcube.services.concept_type import ConceptTypeService
from objectcube.exceptions import (ObjectCubeException,
                                   ObjectCubeDatabaseException)
from objectcube.vo import ConceptType, Concept


class TestConceptService(TestDatabaseAwareTest):
    def __init__(self, *args, **kwargs):
        super(TestConceptService, self).__init__(*args, **kwargs)
        self.concept_service = ConceptService()
        self.concept_type_service = ConceptTypeService()

    def _create_content_type(self, name, base_type, regex=None):
        return ConceptTypeService().\
            add_concept_type(name=name,
                             concept_base_type=base_type,
                             regex_pattern=regex)

    def test_add_concept_raises_exception_if_name_is_missing(self):
        with self.assertRaises(ObjectCubeException,
                               msg='If name is missing, add_concept should '
                                   'raise exception'):
            self.concept_service.add_concept(name=None, concept_type=1)

        with self.assertRaises(ObjectCubeException,
                               msg='If name is missing, add_concept should '
                                   'raise exception'):
            self.concept_service.add_concept(name='', concept_type=1)

    def test_invalid_concept_type_arguments(self):
        with self.assertRaises(ObjectCubeException):
            self.concept_service.add_concept(concept_type='string', name='t')

        with self.assertRaises(ObjectCubeException):
            self.concept_service.add_concept(concept_type='', name='t')

        with self.assertRaises(ObjectCubeException):
            self.concept_service.add_concept(concept_type=None, name='t')

        with self.assertRaises(ObjectCubeException):
            self.concept_service.add_concept(concept_type=4.3, name='t')

    def test_creates_concept_return_concept_object(self):
        ct = self._create_content_type(name='AlphaNumerical',
                                       base_type=ConceptType.ALPHANUMERICAL)

        concept = self.concept_service.add_concept(concept_type=ct,
                                                   name='test_concept')
        self.assertTrue(isinstance(concept, Concept))

    def test_returning_concept_contains_id(self):
        ct = self._create_content_type(name='AlphaNumerical',
                                       base_type=ConceptType.ALPHANUMERICAL)

        concept1 = self.concept_service.add_concept(concept_type=ct,
                                                    name='test_concept1')
        concept2 = self.concept_service.add_concept(concept_type=ct,
                                                    name='test_concept2')
        self.assertTrue(concept1.id == 1,
                        msg='The first created concept should have id 1')
        self.assertTrue(concept2.id == 2,
                        msg='The first created concept should have id 2')

    def test_create_concept_increases_concept_count(self):
        self.assertEquals(self.concept_service.get_concept_count(), 0)
        ct = self._create_content_type(name='Creation date',
                                       base_type=ConceptType.DATETIME)
        self.concept_service.add_concept(concept_type=ct, name='test_concept1')
        self.assertEquals(self.concept_service.get_concept_count(), 1)

    def test_uniqueness_of_concept_name(self):
        concept_name = 'aperture speed'
        self._create_content_type(name=concept_name,
                                  base_type=ConceptType.NUMERICAL)

        with self.assertRaises(ObjectCubeDatabaseException):
            self._create_content_type(name=concept_name,
                                      base_type=ConceptType.ALPHANUMERICAL)

    def test_fetch_concept_by_id(self):
        ct = self._create_content_type(name='Creation date',
                                       base_type=ConceptType.DATETIME)
        concept = self.concept_service.add_concept(concept_type=ct,
                                                   name='test_concept1')

        fresh_concept = self.concept_service.get_concept_by_id(concept.id)
        self.assertEquals(concept, fresh_concept)

    def test_fetch_by_id_not_found_returns_none(self):
        self.assertIsNone(self.concept_service.get_concept_by_id(1000))

    def test_get_by_name(self):
        ct = self._create_content_type(name='Creation date',
                                       base_type=ConceptType.DATETIME)
        concept = self.concept_service.add_concept(concept_type=ct,
                                                   name='test_concept1')

        fresh_concept = self.concept_service.get_concept_by_name(concept.name)
        self.assertEquals(concept, fresh_concept)

    def test_fetch_by_name_not_found_returns_none(self):
        self.assertIsNone(self.concept_service.get_concept_by_name('no name'))

    def test_fetch_all_less_than_offset(self):
        number_created = 5
        ct = self._create_content_type(name='Creation date',
                                       base_type=ConceptType.DATETIME)
        for i in range(number_created):
            self.concept_service.add_concept(ct, 'concept-{0}'.format(i))

        self.assertEquals(len(self.concept_service.get_concepts()),
                          number_created)