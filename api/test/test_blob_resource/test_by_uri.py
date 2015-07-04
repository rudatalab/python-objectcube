import json

from api import app
from api.test import APITest


class TestAPIBlobResourceByURI(APITest):
    def __init__(self, *args, **kwargs):
        super(TestAPIBlobResourceByURI, self).__init__(*args, **kwargs)
        self.base_url = '/api/blobs/uri/'
        self.app = app.test_client()

    def test_get_description_query_parameter_returns_description(self):
        res = self.get(self.base_url + '1?description')
        data = json.loads(res.data)
        self.assertTrue(data.get('endpoint') == 'api/blobs/uri/<digest>')
