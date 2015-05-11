import json
from unittest import TestCase
from objectcube.contexts import Connection


class DatabaseAwareTest(TestCase):
    def __init__(self, *args, **kwargs):
        super(DatabaseAwareTest, self).__init__(*args, **kwargs)

    def setUp(self):
        with open('schema.sql') as fd:
            data = ''.join(fd.readlines())

        with Connection() as c:
            with c.cursor() as cursor:
                cursor.execute(data)


class APITest(DatabaseAwareTest):
    def __init__(self, *args, **kwargs):
        super(APITest, self).__init__(*args, **kwargs)

    def post(self, url, data):
        headers = [('Content-Type', 'application/json')]
        json_data = json.dumps(data)
        headers.append(('Content-Length', json_data))
        return self.app.post(url, headers=headers, data=json_data)

    def get(self, url):
        return self.app.get(url)

    def put(self, url, data):
        headers = [('Content-Type', 'application/json')]
        json_data = json.dumps(data)
        headers.append(('Content-Length', json_data))
        return self.app.put(url, headers=headers, data=json_data)

    def delete(self, url):
        return self.app.delete(url)
