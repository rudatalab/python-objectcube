import json
from api import app
from test_base import APITest


class TestAPIObjectResource(APITest):
    def __init__(self, *args, **kwargs):
        super(TestAPIObjectResource, self).__init__(*args, **kwargs)
        self.base_url = '/api/objects'
        self.app = app.test_client()

    def _post_test_object(self):
        data = {
            'name': 'obj_name'
        }
        res = self.post(self.base_url, data=data)
        self.assertEqual(res.status_code, 201)

    def test_get_objects_route_exists(self):
        res = self.app.get(self.base_url)
        self.assertEqual(res.status_code, 200)

    def test_get_concepts_route_returns_application_json(self):
        res = self.app.get(self.base_url)
        self.assertEqual(res.content_type, 'application/json')

    def test_get_description_query_parameter_returns_description(self):
        res = self.get(self.base_url + '?description')
        data = json.loads(res.data)
        self.assertTrue(data.get('endpoint') == 'api/objects')

    def test_get_objects_response_object_contains_meta(self):
        self._post_test_object()
        data = json.loads(self.get(self.base_url).data)
        self.assertTrue(data.get('meta', False))
        self.assertTrue(data.get('objects', False))

    def test_response_object_contains_concepts(self):
        self._post_test_object()
        data = json.loads(self.get(self.base_url).data)
        self.assertTrue(data.get('objects', False))

    def test_post_with_no_data_returns_400(self):
        res = self.post(self.base_url, data=None)
        self.assertTrue(res.status_code == 400)

    def test_post_with_digest_uses_digest(self):
        data = {
            'name': 'obj_name',
            'digest': 'testdig'
        }
        res = self.post(self.base_url, data=data)
        self.assertEqual(res.status_code, 201)
        data = json.loads(res.data)
        self.assertEqual(data.get('digest'), 'testdig')

    def test_post_with_no_digest_creates_digest(self):
        data = {
            'name': 'obj_name'
        }
        res = self.post(self.base_url, data=data)
        self.assertEqual(res.status_code, 201)
        data = json.loads(res.data)
        self.assertTrue(data.get('digest'), False)

    def test_post_with_no_name_returns_400(self):
        data = {
            'digest': 'testdig'
        }
        res = self.post(self.base_url, data=data)
        self.assertEqual(res.status_code, 400)
