# coding=utf-8
import json

from api import app
from api.test import APITest


class TestAPIConceptResourceGET(APITest):
    def __init__(self, *args, **kwargs):
        super(TestAPIConceptResourceGET, self).__init__(*args, **kwargs)
        self.base_url = '/api/concepts'
        self.app = app.test_client()

    def _post_test_concepts(self, number_to_create=10,
                            title_prefix='concept-'):
        added_concepts = []
        for i in range(number_to_create):
            concept_title = '{}{}'.format(title_prefix, i)

            data = {
                'description': 'description-{}'.format(i),
                'title': concept_title
            }
            res = self.post(self.base_url, data=data)
            self.assertEquals(res.status_code, 201)
            added_concepts.append(concept_title)
        return added_concepts

    def test_concepts_route_exists(self):
        res = self.app.get(self.base_url)
        self.assertEqual(res.status_code, 200)

    def test_concepts_route_returns_application_json(self):
        res = self.app.get(self.base_url)
        self.assertEqual(res.content_type, 'application/json')

    def test_response_object_contains_meta(self):
        self._post_test_concepts()
        data = json.loads(self.get(self.base_url).data)
        self.assertTrue(data.get('meta', False))

    def test_response_object_contains_concepts(self):
        self._post_test_concepts()
        data = json.loads(self.get(self.base_url).data)
        self.assertTrue(data.get('concepts', False))

    def test_response_object_contains_meta_and_concepts(self):
        self._post_test_concepts()
        data = json.loads(self.get(self.base_url).data)
        self.assertTrue(data.get('meta', False))
        self.assertTrue(data.get('concepts', False))

    def test_pagination(self):
        number_of_concepts = 100
        for i in range(number_of_concepts):
            data = {
                'description': 'description-{}'.format(i),
                'title': 'concept-{}'.format(i)
            }
            res = self.post(self.base_url, data=data)
            self.assertEquals(res.status_code, 201)

        for page in [1, 4, 6]:
            for limit in range(5):
                url = self.base_url + '?page={}&limit={}'.format(
                    page, limit
                )

                data = json.loads(self.get(url).data)
                self.assertEquals(limit, len(data.get('concepts')))

                for i, r in enumerate(data.get('concepts')):
                    self.assertEquals(
                        r.get('title'), 'concept-{}'.format(i + (page * limit))
                    )

    def test_description_query_parameter_returns_description(self):
        res = self.get(self.base_url + '?description')
        data = json.loads(res.data)
        self.assertTrue(data.get('endpoint') == 'api/concepts')
