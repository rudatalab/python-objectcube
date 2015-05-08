from random import shuffle

from base import ObjectCubeTestCase
from objectcube.vo import Concept
from objectcube.exceptions import ObjectCubeException
from objectcube.factory import get_service


class TestConceptService(ObjectCubeTestCase):
    def __init__(self, *args, **kwargs):
        super(TestConceptService, self).__init__(*args, **kwargs)
        self.concept_service = get_service('ConceptService')

    def _add_test_concepts(self, titles=None):
        concepts = []
        shuffle(titles)
        for title in titles:
            concept = self._create_test_concept(str(title))
            concepts.append(self.concept_service.add(concept))
        self.assertEquals(len(titles), len(concepts))

        return concepts

    def _tags_to_id_set(self, concepts):
        return set(map(lambda c: c.id, concepts))

    def _create_test_concept(self, title='', description='', concept_id=None):
        return Concept(id=concept_id, title=title, description=description)

    def _create_and_add_test_concept(self, title, description=''):
        test_concept = self._create_test_concept(title=title,
                                                 description=description)

        concept = self.concept_service.add(test_concept)
        self.assertIsNotNone(concept)
        return concept

    def test_count_returns_zero_with_empty_data_store(self):
        self.assertEqual(self.concept_service.count(), 0)

    def test_count_increments_on_add(self):
        self.assertEqual(self.concept_service.count(), 0)
        concept = self._create_test_concept(title='test-concept')
        self.concept_service.add(concept)
        self.assertEqual(self.concept_service.count(), 1)

    def test_add_concepts_returns_concept_with_id(self):
        concept = self._create_test_concept(title='test-concept')
        db_concept = self.concept_service.add(concept)
        self.assertEqual(type(db_concept), type(concept))
        self.assertTrue(db_concept.id > 0)

    def test_add_raises_exception_on_objects_with_ids(self):
        concept = Concept(**{'id': 4, 'title': 'test', 'description': ''})
        with self.assertRaises(ObjectCubeException):
            self.concept_service.add(concept)

    def test_add_raises_exception_when_title_is_missing(self):
        concept = Concept(**{'description': ''})
        with self.assertRaises(ObjectCubeException):
            self.concept_service.add(concept)

    def test_retrieve_by_title_raises_when_title_is_missing(self):
        with self.assertRaises(ObjectCubeException):
            self.concept_service.retrieve_by_title(None)

        with self.assertRaises(ObjectCubeException):
            self.concept_service.retrieve_by_title('')

    def test_retrieve_by_title_returns_none_if_not_found(self):
        self.assertIsNone(
            self.concept_service.retrieve_by_title('does-not-exists'))

    def test_retrieve_by_title_returns_concept(self):
        test_concept_title = 'test-title'
        test_concept = self._create_test_concept(title=test_concept_title,
                                                 description='test')
        self.concept_service.add(test_concept)
        self.assertEqual(
            type(
                self.concept_service.retrieve_by_title(test_concept_title)),
            Concept)

    def test_retrieve_by_title_returns_correct_concept(self):
        test_concept_title = 'test-title'
        test_concept = self._create_test_concept(title=test_concept_title,
                                                 description='test')
        concept = self.concept_service.add(test_concept)
        db_concept = self.concept_service.retrieve_by_title(test_concept_title)

        self.assertTrue(concept is not None)
        self.assertTrue(db_concept is not None)
        self.assertEquals(concept, db_concept)

    def test_retrieve_by_title_raises_when_id_is_missing(self):
        with self.assertRaises(ObjectCubeException):
            self.concept_service.retrieve_by_id(None)

        with self.assertRaises(ObjectCubeException):
            self.concept_service.retrieve_by_id('')

    def test_retrieve_by_id_returns_none_if_not_found(self):
        self.assertIsNone(
            self.concept_service.retrieve_by_id(43534534))

    def test_retrieve_by_id_returns_concept(self):
        test_concept_title = 'test-title'
        test_concept = self._create_test_concept(title=test_concept_title,
                                                 description='test')
        concept = self.concept_service.add(test_concept)
        self.assertEqual(
            type(
                self.concept_service.retrieve_by_id(concept.id)),
            Concept)

    def test_retrieve_by_id_returns_correct_concept(self):
        concept = self._create_and_add_test_concept('test-title')
        db_concept = self.concept_service.retrieve_by_id(concept.id)

        self.assertTrue(concept is not None)
        self.assertTrue(db_concept is not None)
        self.assertEquals(concept, db_concept)

    def test_update_raises_if_concept_missing_id(self):
        with self.assertRaises(ObjectCubeException):
            self.concept_service.update(
                self._create_test_concept(title='test-title'))

    def test_update_raises_if_concept_not_in_data_store(self):
        with self.assertRaises(ObjectCubeException):
            concept = self._create_test_concept(title='test', concept_id=12)
            self.concept_service.update(concept)

    def test_update_raises_if_concept_missing_title(self):
        with self.assertRaises(ObjectCubeException):
            self.concept_service.update(
                self._create_test_concept(concept_id=23))

    def test_update_concept_title(self):
        before_update_title = 'before-title'
        after_update_title = 'after-title'

        before_concept = self._create_and_add_test_concept(before_update_title)
        self.assertEqual(before_update_title, before_concept.title)

        before_concept.title = after_update_title
        after_concept = self.concept_service.update(before_concept)
        db_concept = self.concept_service.retrieve_by_id(before_concept.id)

        self.assertEqual(after_concept.title, after_update_title)
        self.assertEqual(after_concept.id, before_concept.id)
        self.assertEqual(db_concept.title, after_update_title)
        self.assertEqual(db_concept.id, before_concept.id)

    def test_update_description(self):
        before_update_description = 'before-description'
        after_update_description = 'after-description'
        test_title = 'test-title'

        before_concept = self._create_and_add_test_concept(
            title=test_title,
            description=before_update_description
        )

        self.assertEqual(before_update_description, before_concept.description)

        before_concept.description = after_update_description
        after_concept = self.concept_service.update(before_concept)
        db_concept = self.concept_service.retrieve_by_id(before_concept.id)

        self.assertEqual(after_concept.description, after_update_description)
        self.assertEqual(after_concept.id, before_concept.id)
        self.assertEqual(db_concept.description, after_update_description)
        self.assertEqual(db_concept.id, before_concept.id)

    def test_delete_by_id_raise_if_id_is_missing(self):
        with self.assertRaises(ObjectCubeException):
            self.concept_service.delete_by_id(None)

        with self.assertRaises(ObjectCubeException):
            self.concept_service.delete_by_id(0)

        with self.assertRaises(ObjectCubeException):
            self.concept_service.delete_by_id('12')

    def test_delete_by_id_raises_if_concept_not_in_data_store(self):
        with self.assertRaises(ObjectCubeException):
            self.concept_service.delete_by_id(1)

    def test_delete_by_id_removes_concept_from_data_store(self):
        concept = self._create_and_add_test_concept(title='test-concept')
        self.concept_service.delete_by_id(concept.id)
        db_concept = self.concept_service.retrieve_by_id(concept.id)
        self.assertIsNone(db_concept)

    def test_count_decreases_when_concept_is_deleted(self):
        concept = self._create_and_add_test_concept(title='test-concept')
        count_before_delete = self.concept_service.count()
        self.concept_service.delete_by_id(concept.id)
        count_after_delete = self.concept_service.count()
        self.assertEqual(count_after_delete, count_before_delete - 1)

    def test_delete_raises_if_type_not_concept(self):
        with self.assertRaises(Exception):
            self.concept_service.delete(1)

        with self.assertRaises(Exception):
            self.concept_service.delete(None)

        with self.assertRaises(Exception):
            self.concept_service.delete('')

    def test_delete_removes_concept_from_data_store(self):
        concept = self._create_and_add_test_concept(title='test-concept')
        self.concept_service.delete(concept)
        db_concept = self.concept_service.retrieve_by_id(concept.id)
        self.assertIsNone(db_concept)

    def test_retrieve_offset_limit(self):
        number_of_concepts = 43
        max_fetch = 10
        expected_id_set = self._tags_to_id_set(
            self._add_test_concepts(range(number_of_concepts)))
        self.assertEquals(number_of_concepts, len(expected_id_set))

        all_retrieved_set = set()
        offset = 0

        while True:
            tags = self.concept_service.retrieve(offset=offset, limit=max_fetch)
            retrieved_id_set = self._tags_to_id_set(tags)
            self.assertTrue(all_retrieved_set.isdisjoint(retrieved_id_set),
                            msg='ids overlap with previously retrieved tags'
                            ' when there should be no overlap')
            all_retrieved_set.update(retrieved_id_set)
            if len(tags) != max_fetch:
                self.assertEquals(number_of_concepts % max_fetch, len(tags))
                break
            offset += max_fetch
        self.assertEquals(expected_id_set, all_retrieved_set)

    def test_retrieve_or_create_adds_new_concept_if_not_data_store(self):
        concept_test_title = 'test-concept'
        concept_test_description = 'hi mom'
        concept = self._create_test_concept(
            title=concept_test_title,
            description=concept_test_description
        )

        self.assertIsNone(self.concept_service.retrieve_by_title(concept.title))
        fresh_concept = self.concept_service.retrieve_or_create(concept)

        self.assertIsNotNone(fresh_concept)
        self.assertIsNotNone(fresh_concept.id)

        db_concept = self.concept_service.retrieve_by_id(fresh_concept.id)
        self.assertIsNotNone(db_concept)

        self.assertEqual(db_concept, fresh_concept)

        self.assertEqual(concept_test_title, db_concept.title)
        self.assertEqual(concept_test_description, db_concept.description)

    def test_retrieve_or_create_returns_existing_concept_if_found(self):
        concept_test_title = 'test-concept'
        concept_test_description = 'hi mom'

        concept = self._create_and_add_test_concept(
            title=concept_test_title,
            description=concept_test_description
        )

        self.assertIsNotNone(self.concept_service.retrieve_by_id(concept.id))
        db_concept = self.concept_service.retrieve_or_create(concept)
        self.assertEqual(db_concept, concept)

    def test_retrieve_or_create_requires_concept_type(self):
        concept_test_title = 'test-concept'
        before_count = self.concept_service.count()

        with self.assertRaises(Exception):
            fresh_concept = self.concept_service.retrieve_or_create(concept_test_title)

        self.assertEqual(self.concept_service.count(), before_count)

