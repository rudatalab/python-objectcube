# coding=utf-8
import json

from api import app
from api.test import APITest


class TestAPIConceptResourcePOST(APITest):
    def __init__(self, *args, **kwargs):
        super(TestAPIConceptResourcePOST, self).__init__(*args, **kwargs)
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
            added_concepts.append(concept_title)
        return added_concepts

    def test_concepts_returns_400_if_title_is_missing(self):
        data = {
            'description': 'test description'
        }
        res = self.post(self.base_url, data)
        self.assertEqual(res.status_code, 400)

    def test_concepts_returns_400_if_description_is_missing(self):
        data = {
            'title': 'test title'
        }
        res = self.post(self.base_url, data)
        self.assertEqual(res.status_code, 400)

    def test_post_concepts_returns_400_if_no_data(self):
        res = self.post(self.base_url, data=None)
        self.assertTrue(res.status_code == 400)

    def test_concept_returns_201_when_new_concept_is_created(self):
        data = {
            'description': 'test description',
            'title': 'test-title'
        }
        res = self.post(self.base_url, data=data)
        self.assertEquals(res.status_code, 201)

    def test_concept_returns_concept_in_body_when_created(self):
        data = {
            'description': 'test description',
            'title': 'test-title'
        }
        res = self.post(self.base_url, data=data)
        return_concept = json.loads(res.data)
        self.assertIsNotNone(return_concept.get('id'))
        self.assertEqual(return_concept.get('title'), data.get('title'))
        self.assertEqual(
            return_concept.get('description'), data.get('description')
        )

    def test_concept_title_already_in_use_throws_database_error(self):
        data = {
            'description': 'test desc',
            'title': 'title1'
        }
        res = self.post(self.base_url, data=data)
        self.assertTrue(res.status_code == 201)
        data2 = {
            'description': 'test desc2',
            'title': 'title1'
        }
        self.assertRaises(self.post(self.base_url, data=data2))

    def test_with_icelandic_characters_in_title_returns_201(self):
        data = {
            'description': 'test description',
            'title': 'Íslenskað dótarí'
        }
        res = self.post(self.base_url, data=data)
        self.assertEquals(res.status_code, 201)

    def test_icelandic_characters_in_title_saves_correctly(self):
        data = {
            'description': 'test description',
            'title': 'Allir íslenskir stafir íóáéæðúýþö'
        }
        res = self.post(self.base_url, data=data)
        title = json.loads(res.data)['title']
        data_title = data['title'].decode('utf-8')
        self.assertEquals(title, data_title)

    def test_dash_in_title_saves_correctly(self):
        data = {
            'description': 'test description',
            'title': 'Title - with - dashes'
        }
        res = self.post(self.base_url, data=data)
        title = json.loads(res.data)['title']
        data_title = data['title']
        self.assertEquals(title, data_title)

    def test_underscore_in_title_saves_correctly(self):
        data = {
            'description': 'test description',
            'title': 'Title _ with_underscores'
        }
        res = self.post(self.base_url, data=data)
        title = json.loads(res.data)['title']
        data_title = data['title']
        self.assertEquals(title, data_title)

    def test_slash_in_title_saves_correctly(self):
        data = {
            'description': 'test description',
            'title': 'Title / with / slashes'
        }
        res = self.post(self.base_url, data=data)
        title = json.loads(res.data)['title']
        data_title = data['title']
        self.assertEquals(title, data_title)

    def test_dollar_sign_in_title_saves_correctly(self):
        data = {
            'description': 'test description',
            'title': 'Title $ with $ dollar sign'
        }
        res = self.post(self.base_url, data=data)
        title = json.loads(res.data)['title']
        data_title = data['title']
        self.assertEquals(title, data_title)

    def test_hash_in_title_saves_correctly(self):
        data = {
            'description': 'test description',
            'title': 'Title # with # hash'
        }
        res = self.post(self.base_url, data=data)
        title = json.loads(res.data)['title']
        data_title = data['title']
        self.assertEquals(title, data_title)

    def test_at_sign_in_title_saves_correctly(self):
        data = {
            'description': 'test description',
            'title': 'Title @ with @ at sign'
        }
        res = self.post(self.base_url, data=data)
        title = json.loads(res.data)['title']
        data_title = data['title']
        self.assertEquals(title, data_title)

    def test_caret_in_title_saves_correctly(self):
        data = {
            'description': 'test description',
            'title': 'Title ^ with ^ caret'
        }
        res = self.post(self.base_url, data=data)
        title = json.loads(res.data)['title']
        data_title = data['title']
        self.assertEquals(title, data_title)

    def test_ampersand_in_title_saves_correctly(self):
        data = {
            'description': 'test description',
            'title': 'Title & with & ampersand'
        }
        res = self.post(self.base_url, data=data)
        title = json.loads(res.data)['title']
        data_title = data['title']
        self.assertEquals(title, data_title)

    def test_multiplication_in_title_saves_correctly(self):
        data = {
            'description': 'test description',
            'title': 'Title * with * multiplication sign'
        }
        res = self.post(self.base_url, data=data)
        title = json.loads(res.data)['title']
        data_title = data['title']
        self.assertEquals(title, data_title)

    def test_brackets_in_title_saves_correctly(self):
        data = {
            'description': 'test description',
            'title': 'Title [ with ] brackets'
        }
        res = self.post(self.base_url, data=data)
        title = json.loads(res.data)['title']
        data_title = data['title']
        self.assertEquals(title, data_title)

    def test_curly_braces_in_title_saves_correctly(self):
        data = {
            'description': 'test description',
            'title': 'Title { with } curly braces'
        }
        res = self.post(self.base_url, data=data)
        title = json.loads(res.data)['title']
        data_title = data['title']
        self.assertEquals(title, data_title)

    def test_round_brackets_in_title_saves_correctly(self):
        data = {
            'description': 'test description',
            'title': 'Title ( with ) round brackets'
        }
        res = self.post(self.base_url, data=data)
        title = json.loads(res.data)['title']
        data_title = data['title']
        self.assertEquals(title, data_title)

    def test_angle_brackets_in_title_saves_correctly(self):
        data = {
            'description': 'test description',
            'title': 'Title < with > round brackets'
        }
        res = self.post(self.base_url, data=data)
        title = json.loads(res.data)['title']
        data_title = data['title']
        self.assertEquals(title, data_title)

    def test_plus_sign_in_title_saves_correctly(self):
        data = {
            'description': 'test description',
            'title': 'Title + with + plus sign'
        }
        res = self.post(self.base_url, data=data)
        title = json.loads(res.data)['title']
        data_title = data['title']
        self.assertEquals(title, data_title)

    def test_equal_sign_in_title_saves_correctly(self):
        data = {
            'description': 'test description',
            'title': 'Title = with = plus sign'
        }
        res = self.post(self.base_url, data=data)
        title = json.loads(res.data)['title']
        data_title = data['title']
        self.assertEquals(title, data_title)

    def test_icelandic_characters_in_description_saves_correctly(self):
        data = {
            'description': 'Allir íslenskir stafir íóáéæðúýþö',
            'title': 'test title'
        }
        res = self.post(self.base_url, data=data)
        description = json.loads(res.data)['description']
        data_description = data['description'].decode('utf-8')
        self.assertEquals(description, data_description)

    def test_dash_in_description_saves_correctly(self):
        data = {
            'title': 'test title',
            'description': 'Description - with - dashes'
        }
        res = self.post(self.base_url, data=data)
        title = json.loads(res.data)['title']
        data_title = data['title']
        self.assertEquals(title, data_title)

    def test_underscore_in_description_saves_correctly(self):
        data = {
            'title': 'test title',
            'description': 'Description _ with_underscores'
        }
        res = self.post(self.base_url, data=data)
        title = json.loads(res.data)['title']
        data_title = data['title']
        self.assertEquals(title, data_title)

    def test_slash_in_description_saves_correctly(self):
        data = {
            'title': 'test title',
            'description': 'Description / with / slashes'
        }
        res = self.post(self.base_url, data=data)
        title = json.loads(res.data)['title']
        data_title = data['title']
        self.assertEquals(title, data_title)

    def test_dollar_sign_in_description_saves_correctly(self):
        data = {
            'title': 'test title',
            'description': 'Description $ with $ dollar sign'
        }
        res = self.post(self.base_url, data=data)
        title = json.loads(res.data)['title']
        data_title = data['title']
        self.assertEquals(title, data_title)

    def test_hash_in_description_saves_correctly(self):
        data = {
            'title': 'test title',
            'description': 'Description # with # hash'
        }
        res = self.post(self.base_url, data=data)
        title = json.loads(res.data)['title']
        data_title = data['title']
        self.assertEquals(title, data_title)

    def test_at_sign_in_description_saves_correctly(self):
        data = {
            'title': 'test title',
            'description': 'Description @ with @ at sign'
        }
        res = self.post(self.base_url, data=data)
        title = json.loads(res.data)['title']
        data_title = data['title']
        self.assertEquals(title, data_title)

    def test_caret_in_description_saves_correctly(self):
        data = {
            'title': 'test title',
            'description': 'Description ^ with ^ caret'
        }
        res = self.post(self.base_url, data=data)
        title = json.loads(res.data)['title']
        data_title = data['title']
        self.assertEquals(title, data_title)

    def test_ampersand_in_description_saves_correctly(self):
        data = {
            'title': 'test title',
            'description': 'Description & with & ampersand'
        }
        res = self.post(self.base_url, data=data)
        title = json.loads(res.data)['title']
        data_title = data['title']
        self.assertEquals(title, data_title)

    def test_multiplication_in_description_saves_correctly(self):
        data = {
            'title': 'test title',
            'description': 'Description * with * multiplication sign'
        }
        res = self.post(self.base_url, data=data)
        title = json.loads(res.data)['title']
        data_title = data['title']
        self.assertEquals(title, data_title)

    def test_brackets_in_description_saves_correctly(self):
        data = {
            'title': 'test title',
            'description': 'Description [ with ] brackets'
        }
        res = self.post(self.base_url, data=data)
        title = json.loads(res.data)['title']
        data_title = data['title']
        self.assertEquals(title, data_title)

    def test_curly_braces_in_description_saves_correctly(self):
        data = {
            'title': 'test title',
            'description': 'Description { with } curly braces'
        }
        res = self.post(self.base_url, data=data)
        title = json.loads(res.data)['title']
        data_title = data['title']
        self.assertEquals(title, data_title)

    def test_round_brackets_in_description_saves_correctly(self):
        data = {
            'title': 'test title',
            'description': 'Description ( with ) round brackets'
        }
        res = self.post(self.base_url, data=data)
        title = json.loads(res.data)['title']
        data_title = data['title']
        self.assertEquals(title, data_title)

    def test_angle_brackets_in_description_saves_correctly(self):
        data = {
            'title': 'test title',
            'description': 'Description < with > round brackets'
        }
        res = self.post(self.base_url, data=data)
        title = json.loads(res.data)['title']
        data_title = data['title']
        self.assertEquals(title, data_title)

    def test_plus_sign_in_description_saves_correctly(self):
        data = {
            'title': 'test title',
            'description': 'Description + with + plus sign'
        }
        res = self.post(self.base_url, data=data)
        title = json.loads(res.data)['title']
        data_title = data['title']
        self.assertEquals(title, data_title)

    def test_equal_sign_in_description_saves_correctly(self):
        data = {
            'title': 'test title',
            'description': 'Description = with = plus sign'
        }
        res = self.post(self.base_url, data=data)
        title = json.loads(res.data)['title']
        data_title = data['title']
        self.assertEquals(title, data_title)
