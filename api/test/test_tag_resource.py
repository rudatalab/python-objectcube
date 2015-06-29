import json
from api import app
from test_base import APITest


class TestAPITagResource(APITest):
    def __init__(self, *args, **kwargs):
        super(TestAPITagResource, self).__init__(*args, **kwargs)
        self.base_url = '/api/tags'
        self.app = app.test_client()

    def test_get_tags_route_exists(self):
        res = self.app.get(self.base_url)
        self.assertEqual(res.status_code, 200)

    def test_get_tags_route_returns_application_json(self):
        res = self.app.get(self.base_url)
        self.assertEqual(res.content_type, 'application/json')

    def test_get_description_query_parameter_returns_description(self):
        res = self.get(self.base_url + '?description')
        data = json.loads(res.data)
        self.assertTrue(data.get('endpoint') == 'api/tags')

    def test_create_tag_returns_201(self):
        data = {
            'description': 'tag_description',
            'value': 'tag_value',
            'type': 0,
            'mutable': False
        }
        res = self.post(self.base_url, data=data)
        self.assertEqual(res.status_code, 201)

    def test_create_tag_returns_tag(self):
        data = {
            'description': u'tag_description',
            'value': u'tag_value',
            'type': 0L,
            'mutable': True
        }
        res = self.post(self.base_url, data=data)
        res_data = json.loads(res.data)
        self.assertEqual(res_data.get('value'), u'tag_value')
        self.assertEqual(res_data.get('description'), u'tag_description')
        self.assertEqual(res_data.get('type'), 0)

    def test_tag_with_no_value_returns_400(self):
        data = {
            'description': u'tag_description',
            'type': 0
        }
        res = self.post(self.base_url, data=data)
        self.assertEqual(res.status_code, 400)

    def test_tag_with_no_type_returns_400(self):
        data = {
            'description': u'tag_description',
            'value': u'tag_value'
        }
        res = self.post(self.base_url, data=data)
        self.assertEqual(res.status_code, 400)

    def test_post_with_no_data_returns_400(self):
        res = self.post(self.base_url, data=None)
        self.assertTrue(res.status_code == 400)
