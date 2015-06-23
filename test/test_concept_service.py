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
            concept = self._create_test_concept(title=u'Concept'+str(title),
                                                description=u'Desc'+str(title))
            concepts.append(self.concept_service.add(concept))
        self.assertEquals(len(titles), len(concepts))

        return concepts

    def _tags_to_id_set(self, concepts):
        return set(map(lambda c: c.id, concepts))

    def _create_test_concept(self, title=u'', description=u'', id=None):
        return Concept(id=id, title=title, description=description)

    def _create_and_add_test_concept(self, title, description=u''):
        test_concept = self._create_test_concept(title=title,
                                                 description=description)

        concept = self.concept_service.add(test_concept)
        self.assertIsNotNone(concept)
        self.assertIsNotNone(concept.id)
        return concept

    def test_concept_count_returns_zero_with_empty_data_store(self):
        self.assertEqual(self.concept_service.count(), 0)

    def test_concept_count_increments_on_add(self):
        self.assertEqual(self.concept_service.count(), 0)
        concept = self._create_test_concept(title=u'test-concept',
                                            description=u'test-desc')
        self.concept_service.add(concept)
        self.assertEqual(self.concept_service.count(), 1)

    def test_concept_add_concepts_returns_concept_with_id(self):
        concept = self._create_test_concept(title=u'test-concept',
                                            description=u'test-desc')
        db_concept = self.concept_service.add(concept)
        self.assertEqual(type(db_concept), type(concept))
        self.assertTrue(db_concept.id > 0)

    def test_concept_add_raises_exception_on_objects_with_ids(self):
        concept = Concept(**{'id': 4L, 'title': u'test', 'description': u''})
        with self.assertRaises(ObjectCubeException):
            self.concept_service.add(concept)

    def test_concept_add_raises_exception_when_title_is_missing(self):
        with self.assertRaises(ObjectCubeException):
            concept = Concept(**{'description': u''})
            self.concept_service.add(concept)

    def test_concept_retrieve_by_title_raises_with_invalid_title(self):
        with self.assertRaises(ObjectCubeException):
            self.concept_service.retrieve_by_title(None)
        with self.assertRaises(ObjectCubeException):
            self.concept_service.retrieve_by_title(title=0)
        with self.assertRaises(ObjectCubeException):
            self.concept_service.retrieve_by_title(title=-1)
        with self.assertRaises(ObjectCubeException):
            self.concept_service.retrieve_by_title(title=1)
        with self.assertRaises(ObjectCubeException):
            self.concept_service.retrieve_by_title(title=3.1415297)
        with self.assertRaises(ObjectCubeException):
            self.concept_service.retrieve_by_title(title=Concept())

    def test_concept_retrieve_by_regex_raises_with_invalid_regex(self):
        with self.assertRaises(ObjectCubeException):
            self.concept_service.retrieve_by_regex()

        with self.assertRaises(ObjectCubeException):
            self.concept_service.retrieve_by_regex(title=0)
        with self.assertRaises(ObjectCubeException):
            self.concept_service.retrieve_by_regex(title=-1)
        with self.assertRaises(ObjectCubeException):
            self.concept_service.retrieve_by_regex(title=1)
        with self.assertRaises(ObjectCubeException):
            self.concept_service.retrieve_by_regex(title=3.1415297)
        with self.assertRaises(ObjectCubeException):
            self.concept_service.retrieve_by_regex(title=Concept())

        with self.assertRaises(ObjectCubeException):
            self.concept_service.retrieve_by_regex(description=0)
        with self.assertRaises(ObjectCubeException):
            self.concept_service.retrieve_by_regex(description=-1)
        with self.assertRaises(ObjectCubeException):
            self.concept_service.retrieve_by_regex(description=1)
        with self.assertRaises(ObjectCubeException):
            self.concept_service.retrieve_by_regex(description=3.1415297)
        with self.assertRaises(ObjectCubeException):
            self.concept_service.retrieve_by_regex(description=Concept())

    def test_concept_retrieve_by_title_returns_none_if_not_found(self):
        concept = self.concept_service.retrieve_by_title(u'does-not-exists')
        self.assertEquals(concept, None, 'Should be None')

    def test_concept_retrieve_by_title_returns_concept(self):
        test_concept_title = u'test-title'
        test_concept = self._create_test_concept(title=test_concept_title,
                                                 description=u'test')
        self.concept_service.add(test_concept)
        out_concept = self.concept_service.retrieve_by_title(test_concept_title)
        self.assertEqual(type(out_concept), Concept)

    def test_concept_retrieve_by_title_returns_correct_concept(self):
        test_concept_title = u'test-title'
        test_concept = self._create_test_concept(title=test_concept_title,
                                                 description=u'test')
        concept = self.concept_service.add(test_concept)
        db_concept = self.concept_service.retrieve_by_title(test_concept_title)

        self.assertTrue(concept is not None)
        self.assertTrue(db_concept is not None)
        self.assertEquals(concept, db_concept)

    def test_concept_retrieve_by_title_raises_when_id_is_missing(self):
        with self.assertRaises(ObjectCubeException):
            self.concept_service.retrieve_by_id(None)

        with self.assertRaises(ObjectCubeException):
            self.concept_service.retrieve_by_id('')

    def test_concept_retrieve_by_id_returns_none_if_not_found(self):
        self.assertIsNone(self.concept_service.retrieve_by_id(43534534L))

    def test_concept_retrieve_by_id_returns_correct_concept(self):
        test_concept = self._create_test_concept(title=u'test-title',
                                                 description=u'test')
        db_concept = self.concept_service.add(test_concept)
        out_concept = self.concept_service.retrieve_by_id(db_concept.id)

        self.assertEqual(type(out_concept), Concept)
        self.assertEqual(type(db_concept), Concept)
        self.assertTrue(out_concept is not None)
        self.assertTrue(db_concept is not None)
        self.assertEquals(out_concept, db_concept)

    def test_concept_update_raises_if_concept_missing_id(self):
        with self.assertRaises(ObjectCubeException):
            self.concept_service.update(
                self._create_test_concept(title=u'test-title',
                                          description=u'test-desc'))

    def test_concept_update_raises_if_concept_not_in_data_store(self):
        with self.assertRaises(ObjectCubeException):
            concept = self._create_test_concept(title=u'test',
                                                description=u'test',
                                                id=12L)
            self.concept_service.update(concept)

    def test_concept_update_raises_if_concept_missing_title(self):
        # Invalid ID formats
        with self.assertRaises(ObjectCubeException):
            self.concept_service.update(None)
        with self.assertRaises(ObjectCubeException):
            self.concept_service.update(0)
        with self.assertRaises(ObjectCubeException):
            self.concept_service.update(1)
        with self.assertRaises(ObjectCubeException):
            self.concept_service.update('ID')
        with self.assertRaises(ObjectCubeException):
            self.concept_service.update(3.1415297)

        # Invalid title formats
        with self.assertRaises(ObjectCubeException):
            self.concept_service.update(Concept())
        with self.assertRaises(ObjectCubeException):
            self.concept_service.update(Concept(id=23L))
        with self.assertRaises(ObjectCubeException):
            self.concept_service.update(Concept(id=-1L))
        with self.assertRaises(ObjectCubeException):
            self.concept_service.update(Concept(id=1L, title=1))
        with self.assertRaises(ObjectCubeException):
            self.concept_service.update(Concept(id=1L, title=0))
        with self.assertRaises(ObjectCubeException):
            self.concept_service.update(Concept(id=1L, title=3.1415297))
        with self.assertRaises(ObjectCubeException):
            self.concept_service.update(Concept(id=1L, title=Concept()))

        # Invalid description formats
        with self.assertRaises(ObjectCubeException):
            self.concept_service.update(Concept(id=1L, title=u'new'))
        with self.assertRaises(ObjectCubeException):
            self.concept_service.update(Concept(id=1L, title=u'new', description=0))
        with self.assertRaises(ObjectCubeException):
            self.concept_service.update(Concept(id=1L, title=u'new', description=0))
        with self.assertRaises(ObjectCubeException):
            self.concept_service.update(Concept(id=1L, title=u'new', description=3.1415297))
        with self.assertRaises(ObjectCubeException):
            self.concept_service.update(Concept(id=1L, title=u'new', description=Concept()))

    def test_concept_update_concept_title(self):
        before_update_title = u'before-title'
        after_update_title = u'after-title'
        description = u'test-desc'

        before_concept = self._create_and_add_test_concept(title=before_update_title,
                                                           description=description)
        self.assertEqual(before_update_title, before_concept.title)

        before_concept.title = after_update_title
        after_concept = self.concept_service.update(before_concept)
        db_concept = self.concept_service.retrieve_by_id(before_concept.id)

        self.assertEqual(after_concept.title, after_update_title)
        self.assertEqual(after_concept.id, before_concept.id)
        self.assertEqual(db_concept.title, after_update_title)
        self.assertEqual(db_concept.id, before_concept.id)

    def test_concept_update_description(self):
        before_update_description = u'before-description'
        after_update_description = u'after-description'
        test_title = u'test-title'

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

    def test_concept_delete_raises_if_concept_not_in_data_store(self):
        with self.assertRaises(ObjectCubeException):
            self.concept_service.delete(Concept(id=1L))

    def test_concept_delete_by_id_raises_if_concept_not_in_data_store(self):
        with self.assertRaises(ObjectCubeException):
            self.concept_service.delete_by_id(id=1L)

    def test_concept_delete_removes_concept_from_data_store(self):
        concept = self._create_and_add_test_concept(title=u'test-concept',
                                                    description=u'test-desc')
        self.concept_service.delete(concept)
        db_concept = self.concept_service.retrieve_by_id(concept.id)
        self.assertIsNone(db_concept)

    def test_concept_count_decreases_when_concept_is_deleted(self):
        concept = self._create_and_add_test_concept(title=u'test-concept',
                                                    description=u'test-desc')
        count_before_delete = self.concept_service.count()
        self.concept_service.delete(concept)
        count_after_delete = self.concept_service.count()
        self.assertEqual(count_after_delete, count_before_delete - 1)

    def test_concept_delete_raises_if_type_not_concept(self):
        with self.assertRaises(Exception):
            self.concept_service.delete(1)
        with self.assertRaises(Exception):
            self.concept_service.delete(None)
        with self.assertRaises(Exception):
            self.concept_service.delete('')

    def test_concept_delete_raises_if_concept_id_is_invalid(self):
        with self.assertRaises(ObjectCubeException):
            self.concept_service.delete(Concept())
        with self.assertRaises(ObjectCubeException):
            self.concept_service.delete(Concept(id=3.1415297))
        with self.assertRaises(ObjectCubeException):
            self.concept_service.delete(Concept(id='0'))
        with self.assertRaises(ObjectCubeException):
            self.concept_service.delete(Concept(id='1'))
        with self.assertRaises(ObjectCubeException):
            self.concept_service.delete(Concept(id='ID'))
        with self.assertRaises(ObjectCubeException):
            self.concept_service.delete(Concept(id=Concept()))

    def test_concept_delete_removes_concept_from_data_store(self):
        concept = self._create_and_add_test_concept(title=u'test-concept',
                                                    description=u'test-desc')
        self.concept_service.delete(concept)
        db_concept = self.concept_service.retrieve_by_id(concept.id)
        self.assertIsNone(db_concept)

    def test_concept_retrieve_offset_limit(self):
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

    def test_concept_retrieve_or_create_adds_new_concept_if_not_data_store(self):
        concept_test_title = u'test-concept'
        concept_test_description = u'hi mom'
        concept = self._create_test_concept(
            title=concept_test_title,
            description=concept_test_description
        )

        self.assertEquals(self.concept_service.retrieve_by_title(concept.title), None)
        fresh_concept = self.concept_service.retrieve_or_create(concept)

        self.assertIsNotNone(fresh_concept)
        self.assertIsNotNone(fresh_concept.id)

        db_concept = self.concept_service.retrieve_by_id(fresh_concept.id)
        self.assertIsNotNone(db_concept)

        self.assertEqual(db_concept, fresh_concept)

        self.assertEqual(concept_test_title, db_concept.title)
        self.assertEqual(concept_test_description, db_concept.description)

    def test_concept_add_raises_on_illegal_arguments(self):
        with self.assertRaises(ObjectCubeException):
            self.concept_service.add(None)
        with self.assertRaises(ObjectCubeException):
            self.concept_service.add(1)
        with self.assertRaises(ObjectCubeException):
            self.concept_service.add(0)
        with self.assertRaises(ObjectCubeException):
            self.concept_service.add(-1)
        with self.assertRaises(ObjectCubeException):
            self.concept_service.add(3.1415297)
        with self.assertRaises(ObjectCubeException):
            self.concept_service.add(u'ID')
        with self.assertRaises(ObjectCubeException):
            self.concept_service.add(Concept())

        with self.assertRaises(ObjectCubeException):
            self.concept_service.add(Concept(id=1L))
        with self.assertRaises(ObjectCubeException):
            self.concept_service.add(Concept(id=0L))
        with self.assertRaises(ObjectCubeException):
            self.concept_service.add(Concept(id=-1L))
        with self.assertRaises(ObjectCubeException):
            self.concept_service.add(Concept(id=3.1415297))
        with self.assertRaises(ObjectCubeException):
            self.concept_service.add(Concept(id=u'ID'))
        with self.assertRaises(ObjectCubeException):
            self.concept_service.add(Concept(id=Concept()))

        with self.assertRaises(ObjectCubeException):
            self.concept_service.add(Concept(id=1L, title=u'Title', description=u'Description1'))
        with self.assertRaises(ObjectCubeException):
            self.concept_service.add(Concept(id=0L, title=u'Title', description=u'Description1'))
        with self.assertRaises(ObjectCubeException):
            self.concept_service.add(Concept(id=-1L, title=u'Title', description=u'Description1'))
        with self.assertRaises(ObjectCubeException):
            self.concept_service.add(Concept(id=3.1415297, title=u'Title', description=u'Description1'))
        with self.assertRaises(ObjectCubeException):
            self.concept_service.add(Concept(id=u'ID', title=u'Title', description=u'Description1'))
        with self.assertRaises(ObjectCubeException):
            self.concept_service.add(Concept(id=Concept(), title=u'Title', description=u'Description1'  ))

        with self.assertRaises(ObjectCubeException):
            self.concept_service.add(Concept(title=1))
        with self.assertRaises(ObjectCubeException):
            self.concept_service.add(Concept(title=-1))
        with self.assertRaises(ObjectCubeException):
            self.concept_service.add(Concept(title=0))
        with self.assertRaises(ObjectCubeException):
            self.concept_service.add(Concept(title=3.1415297))
        with self.assertRaises(ObjectCubeException):
            self.concept_service.add(Concept(title=Concept()))

        with self.assertRaises(ObjectCubeException):
            self.concept_service.add(Concept(title=u'Title', description=1))
        with self.assertRaises(ObjectCubeException):
            self.concept_service.add(Concept(title=u'Title', description=-1))
        with self.assertRaises(ObjectCubeException):
            self.concept_service.add(Concept(title=u'Title', description=0))
        with self.assertRaises(ObjectCubeException):
            self.concept_service.add(Concept(title=u'Title', description=3.1415297))
        with self.assertRaises(ObjectCubeException):
            self.concept_service.add(Concept(title=u'Title', description=Concept()))

    def test_concept_add_raises_on_duplicate_title(self):
        self.assertEquals(self.concept_service.count(), 0)
        concept1 = Concept(title=u'Title', description=u'Description1')
        concept2 = Concept(title=u'Title', description=u'Description2')

        # First insertion is ok
        concept3=self.concept_service.add(concept1)
        self.assertEquals(concept1.title, concept3.title)
        self.assertEquals(concept1.description, concept3.description)

        with self.assertRaises(ObjectCubeException):
            self.concept_service.add(concept2)
        self.assertEquals(self.concept_service.count(), 1)

    def test_concept_retrieve_or_create_returns_existing_concept_if_found(self):
        concept_test_title = u'test-concept'
        concept_test_description = u'hi mom'

        concept = self._create_and_add_test_concept(
            title=concept_test_title,
            description=concept_test_description
        )

        self.assertIsNotNone(self.concept_service.retrieve_by_id(concept.id))
        db_concept = self.concept_service.retrieve_or_create(concept)
        self.assertEqual(db_concept, concept)

    def test_concept_retrieve_or_create_requires_concept_type(self):
        concept_test_title = u'test-concept'
        before_count = self.concept_service.count()

        with self.assertRaises(Exception):
            fresh_concept = self.concept_service.retrieve_or_create(concept_test_title)

        self.assertEqual(self.concept_service.count(), before_count)

    def test_concept_retrieve_or_create_requires_title(self):
        before_count = self.concept_service.count()

        with self.assertRaises(Exception):
            self.concept_service.retrieve_or_create(Concept())

        with self.assertRaises(Exception):
            self.concept_service.retrieve_or_create(Concept(title=0))
        with self.assertRaises(Exception):
            self.concept_service.retrieve_or_create(Concept(title=1))
        with self.assertRaises(Exception):
            self.concept_service.retrieve_or_create(Concept(title=-1))
        with self.assertRaises(Exception):
            self.concept_service.retrieve_or_create(Concept(title=3.1415297))
        with self.assertRaises(Exception):
            self.concept_service.retrieve_or_create(Concept(title=Concept()))

        self.assertEqual(self.concept_service.count(), before_count)

    def test_concept_retrieve_or_create_does_not_require_description(self):
        before_count = self.concept_service.count()

        test_concept = Concept(title=u'test')
        concept = self.concept_service.retrieve_or_create(test_concept)
        db_concept = self.concept_service.retrieve_or_create(concept)

        self.assertEqual(db_concept.description, '')
        self.assertEqual(self.concept_service.count(), before_count + 1)

    def test_concept_retrieve_or_create_does_uses_description(self):
        before_count = self.concept_service.count()

        test_concept = Concept(title=u'test', description=u'Desc')
        concept = self.concept_service.retrieve_or_create(test_concept)
        db_concept = self.concept_service.retrieve_or_create(concept)

        self.assertEqual(db_concept.description, concept.description)
        self.assertEqual(db_concept.description, test_concept.description)
        self.assertEqual(self.concept_service.count(), before_count + 1)

    def test_concept_retrieve_offset_limit(self):
        number_of_concepts = 43
        max_fetch = 10L
        expected_id_set = self._tags_to_id_set(
            self._add_test_concepts(range(number_of_concepts)))
        self.assertEquals(number_of_concepts, len(expected_id_set))

        all_retrieved_set = set()
        offset = 0L

        while True:
            tags = self.concept_service.retrieve(offset=offset, limit=max_fetch)
            retrieved_id_set = self._tags_to_id_set(tags)
            self.assertTrue(all_retrieved_set.isdisjoint(retrieved_id_set),
                            msg='ids overlap with previously retrieved tags')
            all_retrieved_set.update(retrieved_id_set)
            if len(tags) != max_fetch:
                self.assertEquals(number_of_concepts % max_fetch, len(tags))
                break
            offset += max_fetch
        self.assertEquals(expected_id_set, all_retrieved_set)

    def test_concept_retrieve_by_regex_title_offset_limit(self):
        number_of_concepts = 43
        max_fetch = 10L
        db_concepts = self._add_test_concepts(range(number_of_concepts))
        self.assertEquals(number_of_concepts, len(db_concepts))

        offset = 0L
        while True:
            concepts = self.concept_service.retrieve_by_regex(title=db_concepts[0].title,
                                                              offset=offset, limit=max_fetch)
            if len(concepts) != max_fetch:
                break
            offset += max_fetch
        self.assertEquals(len(concepts), 1, 'Returned too many concepts - name should be unique')

        expected_id_set = self._tags_to_id_set(db_concepts)
        self.assertEquals(number_of_concepts, len(expected_id_set))
        all_retrieved_set = set()
        offset = 0L
        while True:
            concepts = self.concept_service.retrieve_by_regex(title=u'Concept',
                                                              offset=offset, limit=max_fetch)
            retrieved_id_set = self._tags_to_id_set(concepts)
            self.assertTrue(all_retrieved_set.isdisjoint(retrieved_id_set),
                            msg='ids overlap with previously retrieved tags')
            all_retrieved_set.update(retrieved_id_set)
            if len(concepts) != max_fetch:
                self.assertEquals(number_of_concepts % max_fetch, len(concepts))
                break
            offset += max_fetch
        self.assertEquals(expected_id_set, all_retrieved_set,
                          'Returned wrong concepts for regexp')

        offset = 0L
        while True:
            concepts = self.concept_service.retrieve_by_regex(title=u'Unknown name',
                                                              offset=offset, limit=max_fetch)
            if len(concepts) != max_fetch:
                break
            offset += max_fetch
        self.assertEquals(len(concepts), 0, 'Returned too many concepts - name should not exist')

    def test_concept_retrieve_by_regex_description_offset_limit(self):
        number_of_concepts = 43
        max_fetch = 10L
        db_concepts = self._add_test_concepts(range(number_of_concepts))
        self.assertEquals(number_of_concepts, len(db_concepts))

        offset = 0L
        while True:
            concepts = self.concept_service.retrieve_by_regex(description=db_concepts[0].description,
                                                              offset=offset, limit=max_fetch)
            if len(concepts) != max_fetch:
                break
            offset += max_fetch
        self.assertEquals(len(concepts), 1, 'Returned too many concepts - name should be unique')

        expected_id_set = self._tags_to_id_set(db_concepts)
        self.assertEquals(number_of_concepts, len(expected_id_set))
        all_retrieved_set = set()
        offset = 0L
        while True:
            concepts = self.concept_service.retrieve_by_regex(description=u'Desc',
                                                              offset=offset, limit=max_fetch)
            retrieved_id_set = self._tags_to_id_set(concepts)
            self.assertTrue(all_retrieved_set.isdisjoint(retrieved_id_set),
                            msg='ids overlap with previously retrieved tags')
            all_retrieved_set.update(retrieved_id_set)
            if len(concepts) != max_fetch:
                self.assertEquals(number_of_concepts % max_fetch, len(concepts))
                break
            offset += max_fetch
        self.assertEquals(expected_id_set, all_retrieved_set,
                          'Returned wrong concepts for regexp')

        #import pdb; pdb.set_trace()
        all_retrieved_set = set()
        offset = 0L
        while True:
            concepts = self.concept_service.retrieve_by_regex(description=u'Desc1',
                                                              offset=offset, limit=max_fetch)
            retrieved_id_set = self._tags_to_id_set(concepts)
            self.assertTrue(all_retrieved_set.isdisjoint(retrieved_id_set),
                            msg='ids overlap with previously retrieved tags')
            all_retrieved_set.update(retrieved_id_set)
            if len(concepts) != max_fetch:
                break
            offset += max_fetch
        self.assertEquals(len(all_retrieved_set), 11,
                          'Returned wrong concepts for regexp')

        offset = 0L
        while True:
            concepts = self.concept_service.retrieve_by_regex(description=u'Unknown name',
                                                              offset=offset, limit=max_fetch)
            if len(concepts) != max_fetch:
                break
            offset += max_fetch
        self.assertEquals(len(concepts), 0, 'Returned too many concepts - name should not exist')

    def test_concept_retrieve_by_regex_title_description_offset_limit(self):
        number_of_concepts = 43
        max_fetch = 10L
        db_concepts = self._add_test_concepts(range(number_of_concepts))
        self.assertEquals(number_of_concepts, len(db_concepts))

        offset = 0L
        while True:
            concepts = self.concept_service.retrieve_by_regex(title=db_concepts[0].title,
                                                              description=db_concepts[0].description,
                                                              offset=offset, limit=max_fetch)
            if len(concepts) != max_fetch:
                break
            offset += max_fetch
        self.assertEquals(len(concepts), 1, 'Returned too many concepts - name should be unique')

        expected_id_set = self._tags_to_id_set(db_concepts)
        self.assertEquals(number_of_concepts, len(expected_id_set))
        all_retrieved_set = set()
        offset = 0L
        while True:
            concepts = self.concept_service.retrieve_by_regex(title=u'Concept',
                                                              description=u'Desc',
                                                              offset=offset, limit=max_fetch)
            retrieved_id_set = self._tags_to_id_set(concepts)
            self.assertTrue(all_retrieved_set.isdisjoint(retrieved_id_set),
                            msg='ids overlap with previously retrieved tags')
            all_retrieved_set.update(retrieved_id_set)
            if len(concepts) != max_fetch:
                self.assertEquals(number_of_concepts % max_fetch, len(concepts))
                break
            offset += max_fetch
        self.assertEquals(expected_id_set, all_retrieved_set,
                          'Returned wrong concepts for regexp')

        #import pdb; pdb.set_trace()
        all_retrieved_set = set()
        offset = 0L
        while True:
            concepts = self.concept_service.retrieve_by_regex(title=u'Concept15',
                                                              description=u'Desc1',
                                                              offset=offset, limit=max_fetch)
            retrieved_id_set = self._tags_to_id_set(concepts)
            self.assertTrue(all_retrieved_set.isdisjoint(retrieved_id_set),
                            msg='ids overlap with previously retrieved tags')
            all_retrieved_set.update(retrieved_id_set)
            if len(concepts) != max_fetch:
                break
            offset += max_fetch
        self.assertEquals(len(all_retrieved_set), 1,
                          'Returned wrong concepts for regexp')

        offset = 0L
        while True:
            concepts = self.concept_service.retrieve_by_regex(title=u'Concept15',
                                                              description=u'Unknown desc',
                                                              offset=offset, limit=max_fetch)
            if len(concepts) != max_fetch:
                break
            offset += max_fetch
        self.assertEquals(len(concepts), 0, 'Returned too many concepts - name should not exist')

    def test_concept_retrieve_by_regex_raises_on_invalid_limit_offset(self):
        self.assertEquals(0, self.concept_service.count(), msg='Database is not empty in beginning')
        db_concept = self.concept_service.add(Concept(title=u'Concept', description=u'Desc'))

        with self.assertRaises(ObjectCubeException):
            self.concept_service.retrieve_by_regex(title=db_concept.title, offset=-1)
        with self.assertRaises(ObjectCubeException):
            self.concept_service.retrieve_by_regex(title=db_concept.title, offset='0')
        with self.assertRaises(ObjectCubeException):
            self.concept_service.retrieve_by_regex(title=db_concept.title, offset='ID')
        with self.assertRaises(ObjectCubeException):
            self.concept_service.retrieve_by_regex(title=db_concept.title, offset=3.1415297)
        with self.assertRaises(ObjectCubeException):
            self.concept_service.retrieve_by_regex(title=db_concept.title, offset=Concept(id=0))

        with self.assertRaises(ObjectCubeException):
            self.concept_service.retrieve_by_regex(title=db_concept.title, limit=-1)
        with self.assertRaises(ObjectCubeException):
            self.concept_service.retrieve_by_regex(title=db_concept.title, limit='0')
        with self.assertRaises(ObjectCubeException):
            self.concept_service.retrieve_by_regex(title=db_concept.title, limit='ID')
        with self.assertRaises(ObjectCubeException):
            self.concept_service.retrieve_by_regex(title=db_concept.title, limit=3.1415297)
        with self.assertRaises(ObjectCubeException):
            self.concept_service.retrieve_by_regex(title=db_concept.title, limit=Concept(id=0))

    def test_concept_retrieve_raises_on_invalid_limit_offset(self):
        self.assertEquals(0, self.concept_service.count(), msg='Database is not empty in beginning')
        db_concept = self.concept_service.add(Concept(title=u'Concept', description=u'Desc'))

        with self.assertRaises(ObjectCubeException):
            self.concept_service.retrieve(offset=-1)
        with self.assertRaises(ObjectCubeException):
            self.concept_service.retrieve(offset='0')
        with self.assertRaises(ObjectCubeException):
            self.concept_service.retrieve(offset='ID')
        with self.assertRaises(ObjectCubeException):
            self.concept_service.retrieve(offset=3.1415297)
        with self.assertRaises(ObjectCubeException):
            self.concept_service.retrieve(offset=Concept(id=0))

        with self.assertRaises(ObjectCubeException):
            self.concept_service.retrieve(limit=-1)
        with self.assertRaises(ObjectCubeException):
            self.concept_service.retrieve(limit='0')
        with self.assertRaises(ObjectCubeException):
            self.concept_service.retrieve(limit='ID')
        with self.assertRaises(ObjectCubeException):
            self.concept_service.retrieve(limit=3.1415297)
        with self.assertRaises(ObjectCubeException):
            self.concept_service.retrieve(limit=Concept(id=0))

    def test_concept_delete_by_id_raises_if_id_is_missing(self):
        with self.assertRaises(ObjectCubeException):
            self.concept_service.delete_by_id(None)
        with self.assertRaises(ObjectCubeException):
            self.concept_service.delete_by_id(0)
        with self.assertRaises(ObjectCubeException):
            self.concept_service.delete_by_id('12')

    def test_concept_delete_by_id_removes_concept_from_data_store(self):
        concept = self._create_and_add_test_concept(title=u'test-concept',
                                                    description=u'test-desc')
        self.concept_service.delete_by_id(concept.id)
        db_concept = self.concept_service.retrieve_by_id(concept.id)
        self.assertIsNone(db_concept)

    def test_concept_count_decreases_when_concept_is_deleted(self):
        concept = self._create_and_add_test_concept(title=u'test-concept',
                                                    description=u'test-desc')
        count_before_delete = self.concept_service.count()
        self.concept_service.delete_by_id(concept.id)
        count_after_delete = self.concept_service.count()
        self.assertEqual(count_after_delete, count_before_delete - 1)


