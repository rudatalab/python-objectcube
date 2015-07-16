from api import app
from api.test import APITest


class TestAPIConceptResourceByIDDELETE(APITest):
    def __init__(self, *args, **kwargs):
        super(TestAPIConceptResourceByIDDELETE, self).__init__(*args, **kwargs)
        self.base_url = '/api/concepts'
        self.app = app.test_client()

    def test_delete_concept_deletes_concept_and_returns_204(self):
        data = {
            'description': 'test desc',
            'title': 'title1'
        }
        res = self.post(self.base_url, data=data)
        self.assertTrue(res.status_code == 201)
        res = self.delete(self.base_url + '/1')
        self.assertTrue(res.status_code == 204)
        res = self.get(self.base_url + '/1')
        self.assertTrue(res.status_code == 404)

    def test_delete_invalid_concept_returns_404(self):
        res = self.delete(self.base_url + '/1')
        self.assertTrue(res.status_code == 404)
