import json

from api import app
from api.test import APITest


class TestAPIObjectResourceByID(APITest):
    def __init__(self, *args, **kwargs):
        super(TestAPIObjectResourceByID, self).__init__(*args, **kwargs)
        self.base_url = '/api/objects'
        self.app = app.test_client()

    def _create_test_object(self):
        data = {
            'name': u'obj_name',
            'digest': u'testdig'
        }
        res = self.post(self.base_url, data=data)
        self.assertEqual(res.status_code, 201)

    def test_get_object_by_id_with_invalid_id_returns_404(self):
        res = self.get(self.base_url + '/1')
        self.assertEqual(res.status_code, 404)

    def test_get_object_by_id_returns_object_and_meta(self):
        self._create_test_object()
        fetch = self.get(self.base_url + '/1')
        final = json.loads(fetch.data)
        self.assertTrue(final.get(u'meta', False))
        self.assertTrue(final.get(u'object', False))

    def test_get_description_query_parameter_returns_description(self):
        res = self.get(self.base_url + '/1?description')
        data = json.loads(res.data)
        self.assertTrue(data.get('endpoint') == 'api/objects/<int:id>')

    def test_update_object_name_returns_updated_information(self):
        self._create_test_object()
        updated_data = {
            'name': u'dummy'
        }
        edit = self.put(self.base_url + '/1', data=updated_data)
        final = json.loads(edit.data)
        self.assertEqual(edit.status_code, 200)
        self.assertEqual(final.get('name'), u'dummy')

    def test_put_with_no_data_returns_400(self):
        res = self.put(self.base_url + '/1', data=None)
        self.assertTrue(res.status_code == 400)

    def test_update_object_by_id_without_required_params_returns_400(self):
        self._create_test_object()
        updated_data = {
            'test': 'fail'
        }
        edit = self.put(self.base_url + '/1', data=updated_data)
        self.assertEqual(edit.status_code, 400)

    def test_updating_object_by_id_that_doesnt_exist_returns_404(self):
        self._create_test_object()
        updated_data = {
            'name': u'dummy'
        }
        edit = self.put(self.base_url + '/500', data=updated_data)
        self.assertEqual(edit.status_code, 404)

    def test_delete_object_deletes_object_and_returns_204(self):
        self._create_test_object()
        res = self.delete(self.base_url + '/1')
        self.assertTrue(res.status_code == 204)
        res = self.get(self.base_url + '/1')
        self.assertTrue(res.status_code == 404)

    def test_delete_invalid_object_returns_404(self):
        res = self.delete(self.base_url + '/1')
        self.assertTrue(res.status_code == 404)
