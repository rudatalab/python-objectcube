import unittest
import json
from objectcube.contexts import Connection
from api import app


class TestDatabaseAwareTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestDatabaseAwareTest, self).__init__(*args, **kwargs)

    def setUp(self):
        with open('schema.sql') as fd:
            data = ''.join(fd.readlines())

        with Connection() as c:
            with c.cursor() as cursor:
                cursor.execute(data)


class APITest(TestDatabaseAwareTest):
    def __init__(self, *args, **kwargs):
        super(APITest, self).__init__(*args, **kwargs)

    def post(self, url, data):
        headers = [('Content-Type', 'application/json')]
        json_data = json.dumps(data)
        headers.append(('Content-Length', json_data))
        return self.app.post(url, headers=headers, data=json_data)

    def get(self, url):
        return self.app.get(url)


class TestConceptServiceAPI(APITest):
    def __init__(self, *args, **kwargs):
        super(TestConceptServiceAPI, self).__init__(*args, **kwargs)
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
