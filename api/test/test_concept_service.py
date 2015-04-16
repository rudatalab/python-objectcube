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


class TestConceptServiceAPI(TestDatabaseAwareTest):
    def __init__(self, *args, **kwargs):
        super(TestConceptServiceAPI, self).__init__(*args, **kwargs)
        self.base_url = '/concepts'
        self.app = app.test_client()

    def _post_data(self, url, data):
        headers = [('Content-Type', 'application/json')]
        json_data = json.dumps(data)
        headers.append(('Content-Length', json_data))
        return self.app.post(url, headers=headers, data=json_data)

    def test_get_concepts_route_exists(self):
        res = self.app.get(self.base_url)
        self.assertEqual(res.status_code, 200)

    def test_get_concepts_route_returns_application_json(self):
        res = self.app.get(self.base_url)
        self.assertEqual(res.content_type, 'application/json')

    def test_post_concepts_returns_400_if_title_is_missing(self):
        data = {'description': 'test description'}
        res = self._post_data(self.base_url, data)
        self.assertEqual(res.status_code, 400)

    def test_post_concept_returns_201_when_new_concept_is_created(self):
        data = {'description': 'test description',
                'title': 'test-title'}
        res = self._post_data(self.base_url, data=data)
        self.assertEquals(res.status_code, 201)

    def test_post_concept_returns_concept_in_body_when_created(self):
        data = {
            'description': 'test description',
            'title': 'test-title'
        }
        res = self._post_data(self.base_url, data=data)
        return_concept = json.loads(res.data)
        self.assertIsNotNone(return_concept.get('id'))
        self.assertEqual(return_concept.get('title'), data.get('title'))
        self.assertEqual(return_concept.get('description'),
                         data.get('description'))
