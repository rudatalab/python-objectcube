import json

from api import app
from api.test import APITest


class TestAPITagResourceByID(APITest):
    def __init__(self, *args, **kwargs):
        super(TestAPITagResourceByID, self).__init__(*args, **kwargs)
        self.base_url = '/api/tags'
        self.app = app.test_client()

    def _create_test_tag(self):
        data = {
            'description': 'tag_description',
            'value': 'tag_value',
            'type': 0,
            'mutable': True
        }
        res = self.post(self.base_url, data=data)
        self.assertEquals(res.status_code, 201)

    def test_get_tag_by_id_with_invalid_id_returns_404(self):
        res = self.get(self.base_url + '/1')
        self.assertEqual(res.status_code, 404)

    def test_get_tag_by_id_returns_tag_and_meta(self):
        self._create_test_tag()
        fetch = self.get(self.base_url + '/1')
        final = json.loads(fetch.data)
        self.assertTrue(final.get('meta', False))
        self.assertTrue(final.get('tag', False))

    def test_get_description_query_parameter_returns_description(self):
        res = self.get(self.base_url + '/1?description')
        data = json.loads(res.data)
        self.assertTrue(data.get('endpoint') == 'api/tags/<int:id>')

    def test_update_tag_description_returns_updated_information(self):
        self._create_test_tag()
        updated_data = {
            'description': 'tag_description2'
        }
        edit = self.put(self.base_url + '/1', data=updated_data)
        final = json.loads(edit.data)
        self.assertEqual(edit.status_code, 200)
        self.assertEqual(final.get('description'), 'tag_description2')

    def test_update_tag_type_returns_updated_information(self):
        self._create_test_tag()
        updated_data = {
            'type': 5
        }
        edit = self.put(self.base_url + '/1', data=updated_data)
        final = json.loads(edit.data)
        self.assertEqual(edit.status_code, 200)
        self.assertEqual(final.get('type'), 5)

    def test_update_tag_value_returns_updated_information(self):
        self._create_test_tag()
        updated_data = {
            'value': 'tag_value2'
        }
        edit = self.put(self.base_url + '/1', data=updated_data)
        final = json.loads(edit.data)
        self.assertEqual(edit.status_code, 200)
        self.assertEqual(final.get('value'), 'tag_value2')

    def test_put_with_no_data_returns_400(self):
        res = self.put(self.base_url + '/1', data=None)
        self.assertTrue(res.status_code == 400)

    def test_update_tag_by_id_without_required_params_returns_400(self):
        self._create_test_tag()
        updated_data = {
            'test': 'fail'
        }
        edit = self.put(self.base_url + '/1', data=updated_data)
        self.assertEqual(edit.status_code, 400)

    def test_updating_tag_by_id_that_doesnt_exist_returns_404(self):
        self._create_test_tag()
        updated_data = {
            'value': 'tag_value2'
        }
        edit = self.put(self.base_url + '/500', data=updated_data)
        self.assertEqual(edit.status_code, 404)

    def test_delete_tag_deletes_tag_and_returns_204(self):
        self._create_test_tag()
        res = self.delete(self.base_url + '/1')
        self.assertTrue(res.status_code == 204)
        res = self.get(self.base_url + '/1')
        self.assertTrue(res.status_code == 404)

    def test_delete_invalid_tag_returns_404(self):
        res = self.delete(self.base_url + '/1')
        self.assertTrue(res.status_code == 404)
