import json

from api import app
from api.test import APITest


class TestAPIConceptResourceByIDGET(APITest):
    def __init__(self, *args, **kwargs):
        super(TestAPIConceptResourceByIDGET, self).__init__(*args, **kwargs)
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
            added_concepts.append(json.loads(res.data))
        return added_concepts

    def test_get_concept_by_id_with_invalid_id_returns_404(self):
        res = self.get(self.base_url + '/1')
        self.assertEqual(res.status_code, 404)

    def test_get_concept_by_id_returns_status_200(self):
        concept = self._post_test_concepts(number_to_create=1)[0]
        res = self.get(self.base_url + '/{}'.format(concept['id']))
        self.assertEqual(res.status_code, 200)

    def test_get_concept_by_id_returns_meta(self):
        concept = self._post_test_concepts(number_to_create=1)[0]
        res = self.get(self.base_url + '/{}'.format(concept['id']))
        data = json.loads(res.data)
        self.assertTrue(data.get('meta', True))

    def test_get_concept_by_id_returns_concepts(self):
        concept = self._post_test_concepts(number_to_create=1)[0]
        res = self.get(self.base_url + '/{}'.format(concept['id']))
        data = json.loads(res.data)
        self.assertTrue(data.get('concepts', True))

    def test_get_concepts_route_returns_application_json(self):
        concept = self._post_test_concepts(number_to_create=1)[0]
        res = self.get(self.base_url + '/{}'.format(concept['id']))
        self.assertEqual(res.content_type, 'application/json')

    def test_get_description_query_parameter_returns_description(self):
        res = self.get(self.base_url + '/1?description')
        data = json.loads(res.data)
        self.assertTrue(data.get('endpoint') == 'api/concepts/<int:id>')
