import json

from api import app
from api.test import APITest


class TestAPITagResourceByValue(APITest):
    def __init__(self, *args, **kwargs):
        super(TestAPITagResourceByValue, self).__init__(*args, **kwargs)
        self.base_url = '/api/tags/values'
        self.app = app.test_client()

    def _create_test_tag(self):
        data = {
            'description': 'tag_description',
            'value': 'tag_value',
            'type': 0,
            'mutable': True
        }
        res = self.post('/api/tags', data=data)
        self.assertEquals(res.status_code, 201)

    def test_get_description_query_parameter_returns_description(self):
        res = self.get(self.base_url + '?description')
        data = json.loads(res.data)
        self.assertTrue(data.get('endpoint') == 'api/tags/values')

    def test_get_tag_by_value_with_no_value_returns_400(self):
        res = self.get(self.base_url)
        self.assertTrue(res.status_code == 400)

    def test_get_tag_by_value_that_exists_returns_200(self):
        self._create_test_tag()
        res = self.get(self.base_url + '?value=tag_value')
        self.assertTrue(res.status_code == 200)

    def test_get_tag_by_value_that_doesnt_exist_returns_404(self):
        self._create_test_tag()
        res = self.get(self.base_url + '?value=test')
        self.assertTrue(res.status_code == 404)

    def test_get_tag_by_value_returns_tag_and_meta(self):
        self._create_test_tag()
        fetch = self.get(self.base_url + '?value=tag_value')
        final = json.loads(fetch.data)
        self.assertTrue(final.get('meta', False))
        self.assertTrue(final.get('tags', False))
