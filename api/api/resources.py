import json
import datetime

from flask.ext import restful
from flask import request

from objectcube.vo import Concept
from objectcube.factory import get_service


class ConceptsResourceList(restful.Resource):
    def __init__(self, *args, **kwargs):
        super(ConceptsResourceList, self).__init__(*args, **kwargs)
        self.concept_service = get_service('ConceptService')
        self.ep_name = 'concepts'

    def get(self):
        limit = long(request.args.get('limit', 100))

        offset = long(request.args.get('offset', 0)) + limit
        a = datetime.datetime.now()
        concept_count = self.concept_service.count()
        concepts = [t.to_dict() for
                    t in self.concept_service.retrieve(
                        limit=limit, offset=offset)]
        b = datetime.datetime.now()

        response_object = {
            'meta': {
                'time': (b - a).microseconds / 1000.0,
                'count': concept_count,
                'next': self.ep_name + '?limit={}&offset={}'
                .format(limit, offset + 1)
            },
            'concepts': concepts,
        }

        return response_object

    def post(self):
        data = json.loads(request.data)
        title = data.get('title')
        description = data.get('description', '')

        if not title:
            return 'Concept must have a title', 400
        try:
            concept = self.concept_service.add(
                Concept(title=title, description=description))
        except Exception as ex:
            return ex.message, 401
        return concept.to_dict(), 201
