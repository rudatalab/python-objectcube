import json

from api import app
from api.test import APITest


class TestAPIConceptResourceByIDPUT(APITest):
    def __init__(self, *args, **kwargs):
        super(TestAPIConceptResourceByIDPUT, self).__init__(*args, **kwargs)
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
            added_concepts.append(json.loads(res.data))
        return added_concepts

    def test_update_concept_with_no_data_returns_400(self):
        headers = [('Content-Type', 'application/json')]
        res = self.app.put(self.base_url + '/1', headers=headers, data=None)
        self.assertEqual(res.status_code, 400)

    def test_update_with_no_title_and_no_description_400(self):
        res = self.put(self.base_url + '/1', data={'lol': 'wut'})
        self.assertEqual(res.status_code, 400)

    def test_update_with_new_title_returns_updated_concept(self):
        data = {
            'description': 'test desc',
            'title': 'title1'
        }
        self.post(self.base_url, data=data)
        updated_data = {'title': 'title2'}
        res = self.put(self.base_url + '/1', data=updated_data)
        final = json.loads(res.data)
        self.assertTrue(final.get('title') == 'title2')
        self.assertTrue(final.get('description') == 'test desc')

    def test_update_with_new_description_returns_updated_concept(self):
        data = {
            'description': 'test desc',
            'title': 'title1'
        }
        self.post(self.base_url, data=data)
        updated_data = {'description': 'desc2'}
        res = self.put(self.base_url + '/1', data=updated_data)
        final = json.loads(res.data)
        self.assertTrue(final.get('description') == 'desc2')
        self.assertTrue(final.get('title') == 'title1')

    def test_update_with_invalid_id_returns_404(self):
        data = {
            'description': 'test desc',
            'title': 'title1'
        }
        res = self.put(self.base_url + '/42', data=data)
        self.assertTrue(res.status_code == 404)

    def test_update_title_is_already_in_use_throws_database_error(self):
        data = {
            'description': 'test desc',
            'title': 'title1'
        }
        res = self.post(self.base_url, data=data)
        data2 = {
            'description': 'test desc2',
            'title': 'title2'
        }
        res2 = self.post(self.base_url, data=data2)
        self.assertTrue(res.status_code == 201)
        self.assertTrue(res2.status_code == 201)
        edit = {'title': 'title1'}
        self.assertRaises(self.put(self.base_url + '/1', data=edit))
