import json
from api import app
from test_base import APITest


class TestAPIConceptResourceByID(APITest):
    def __init__(self, *args, **kwargs):
        super(TestAPIConceptResourceByID, self).__init__(*args, **kwargs)
        self.base_url = '/api/concepts'
        self.app = app.test_client()

    def _post_test_concepts(self, number_to_create=10,
                            title_prefix=u'concept-'):
        added_concepts = []
        for i in range(number_to_create):
            concept_title = u'{}{}'.format(title_prefix, i)

            data = {
                'description': u'description-{}'.format(i),
                'title': concept_title
            }
            res = self.post(self.base_url, data=data)
            self.assertEquals(res.status_code, 201)
            added_concepts.append(json.loads(res.data))
        return added_concepts

    def test_get_concept_by_id_with_invalid_id_returns_404(self):
        res = self.get(self.base_url + '/1')
        self.assertEqual(res.status_code, 404)

    def test_get_concept_by_id_returns_meta_and_concept(self):
        concept = self._post_test_concepts(number_to_create=1)[0]
        res = self.get(self.base_url + '/{}'.format(concept['id']))
        data = json.loads(res.data)
        self.assertTrue(data.get(u'meta', True))
        self.assertTrue(data.get(u'concepts', True))
        self.assertEqual(res.status_code, 200)

    def test_get_concepts_route_returns_application_json(self):
        concept = self._post_test_concepts(number_to_create=1)[0]
        res = self.get(self.base_url + '/{}'.format(concept['id']))
        self.assertEqual(res.content_type, 'application/json')

    def test_get_description_query_parameter_returns_description(self):
        res = self.get(self.base_url + '/1?description')
        data = json.loads(res.data)
        self.assertTrue(data.get('endpoint') == 'api/concepts/<int:id>')

    def test_update_concept_with_no_data_returns_400(self):
        headers = [('Content-Type', 'application/json')]
        res = self.app.put(self.base_url + '/1', headers=headers, data=None)
        self.assertEqual(res.status_code, 400)

    def test_update_with_no_title_and_no_description_400(self):
        res = self.put(self.base_url + '/1', data={'lol': 'wut'})
        self.assertEqual(res.status_code, 400)

    def test_update_with_new_title_returns_updated_concept(self):
        data = {'description': u'test desc', 'title': u'title1'}
        self.post(self.base_url, data=data)
        updated_data = {'title': u'title2'}
        res = self.put(self.base_url + '/1', data=updated_data)
        final = json.loads(res.data)
        self.assertTrue(final.get('title') == 'title2')
        self.assertTrue(final.get('description') ==  'test desc')

    def test_update_with_new_description_returns_updated_concept(self):
        data = {'description': u'test desc', 'title': u'title1'}
        self.post(self.base_url, data=data)
        updated_data = {'description': u'desc2'}
        res = self.put(self.base_url + '/1', data=updated_data)
        final = json.loads(res.data)
        self.assertTrue(final.get('description') == u'desc2')
        self.assertTrue(final.get('title') == u'title1')

    def test_update_with_invalid_id_returns_404(self):
        data = {'description': u'test desc', 'title': u'title1'}
        res = self.put(self.base_url + '/42', data=data)
        self.assertTrue(res.status_code == 404)

    def test_delete_concept_deletes_concept_and_returns_204(self):
        data = {'description': u'test desc', 'title': u'title1'}
        res = self.post(self.base_url, data=data)
        self.assertTrue(res.status_code == 201)
        res = self.delete(self.base_url + '/1')
        self.assertTrue(res.status_code == 204)
        res = self.get(self.base_url + '/1')
        self.assertTrue(res.status_code == 404)

    def test_delete_invalid_concept_returns_404(self):
        res = self.delete(self.base_url + '/1')
        self.assertTrue(res.status_code == 404)

    def test_update_title_is_already_in_use_throws_database_error(self):
        data = {'description': u'test desc', 'title': u'title1'}
        res = self.post(self.base_url, data=data)
        data2 = {'description': u'test desc2', 'title': u'title2'}
        res2 = self.post(self.base_url, data=data2)
        self.assertTrue(res.status_code == 201)
        self.assertTrue(res2.status_code == 201)
        edit = {'title': u'title1'}
        self.assertRaises(self.put(self.base_url + '/1', data=edit))
