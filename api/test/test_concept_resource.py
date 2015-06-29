import json
from api import app
from test_base import APITest


class TestAPIConceptResource(APITest):
    def __init__(self, *args, **kwargs):
        super(TestAPIConceptResource, self).__init__(*args, **kwargs)
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

    def test_get_concepts_route_exists(self):
        res = self.app.get(self.base_url)
        self.assertEqual(res.status_code, 200)

    def test_get_concepts_route_returns_application_json(self):
        res = self.app.get(self.base_url)
        self.assertEqual(res.content_type, 'application/json')

    def test_post_concepts_returns_400_if_title_is_missing(self):
        data = {'description': 'test description'}
        res = self.post(self.base_url, data)
        self.assertEqual(res.status_code, 400)

    def test_post_concept_returns_201_when_new_concept_is_created(self):
        data = {'description': 'test description',
                'title': 'test-title'}
        res = self.post(self.base_url, data=data)
        self.assertEquals(res.status_code, 201)

    def test_post_concept_returns_concept_in_body_when_created(self):
        data = {
            'description': 'test description',
            'title': 'test-title'
        }
        res = self.post(self.base_url, data=data)
        return_concept = json.loads(res.data)
        self.assertIsNotNone(return_concept.get('id'))
        self.assertEqual(return_concept.get('title'), data.get('title'))
        self.assertEqual(return_concept.get('description'),
                         data.get('description'))

    def test_response_object_contains_meta(self):
        self._post_test_concepts()
        data = json.loads(self.get(self.base_url).data)
        self.assertTrue(data.get('meta', False))
        self.assertTrue(data.get('concepts', False))

    def test_response_object_contains_concepts(self):
        self._post_test_concepts()
        data = json.loads(self.get(self.base_url).data)
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
                    self.assertEquals(r.get('title'), 'concept-{}'.format(
                        i + (page * limit))
                    )

    def test_get_description_query_parameter_returns_description(self):
        res = self.get(self.base_url + '?description')
        data = json.loads(res.data)
        self.assertTrue(data.get('endpoint') == 'api/concepts')

    def test_post_with_no_data_returns_400(self):
        res = self.post(self.base_url, data=None)
        self.assertTrue(res.status_code == 400)

    def test_create_concept_title_already_in_use_throws_database_error(self):
        data = {'description': 'test desc', 'title': 'title1'}
        res = self.post(self.base_url, data=data)
        self.assertTrue(res.status_code == 201)
        data2 = {'description': 'test desc2', 'title': 'title1'}
        self.assertRaises(self.post(self.base_url, data=data2))