import unittest
import json
from objectcube.contexts import Connection
from api import app


class TestDatabaseAwareTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestDatabaseAwareTest, self).__init__(*args, **kwargs)

    # XXX: move to some base class.
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

    # XXX: Move to some base class.
    def _post_data(self, url, data):
        headers = [('Content-Type', 'application/json')]
        json_data = json.dumps(data)
        headers.append(('Content-Length', json_data))
        return self.app.post(url, headers=headers, data=json_data)

    def _get_data(self, url):
        # headers = [('Content-Type', 'application/json')]
        # headers.append(('Content-Length', json_data))
        return self.app.get(url)

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

    def test_response_object(self):
        number_of_concepts = 1
        for i in range(number_of_concepts):
            data = {
                'description': 'description-{}'.format(i),
                'title': 'concept-{}'.format(i)
            }
            res = self._post_data(self.base_url, data=data)
            self.assertEquals(res.status_code, 201)

        data = json.loads(self._get_data(self.base_url).data)
        self.assertTrue(data.get('meta', False))
        self.assertTrue(data.get('concepts', False))
        self.assertEquals(number_of_concepts, len(data.get('concepts')))

    def test_pagination(self):
        number_of_concepts = 1500
        for i in range(number_of_concepts):
            data = {
                'description': 'description-{}'.format(i),
                'title': 'concept-{}'.format(i)
            }
            res = self._post_data(self.base_url, data=data)
            self.assertEquals(res.status_code, 201)

        for offset in [0, 4, 6]:
            for limit in [0, 7, 10, 100, 235]:
                url = self.base_url + '?limit={}&offset={}'.format(
                    limit, offset
                )
                data = json.loads(self._get_data(url).data)

                self.assertEquals(limit, len(data.get('concepts')))

                for i, r in enumerate(data.get('concepts')):
                    self.assertEquals(r.get('title'), 'concept-{}'.format(
                        i + offset)
                    )
