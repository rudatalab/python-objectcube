import json
import datetime

from flask.ext import restful
from flask import request

from objectcube.vo import Concept
from objectcube.factory import get_service

from meta import add_meta


def api_metable(orginal_class):
    add_meta(orginal_class.ep_name, orginal_class.description)
    return orginal_class


@api_metable
class ConceptsResourceList(restful.Resource):
    ep_name = 'api/concepts'

    description = {
        'endpoint': ep_name,
        'title': 'Concepts',
        'description': 'Endpoint for fetching and creating concepts',
        'methods': {
            'get': {
                'params': [
                    {
                        'name': 'limit',
                        'type': 'number',
                        'required': False,
                        'min': 0,
                        'default': 20,
                        'description': 'Some human description'
                    },
                    {
                        'name': 'page',
                        'type': 'number',
                        'required': False,
                        'min': 0,
                        'default': 0,
                        'description': 'Some human description'
                    },
                ]
            },
            'post': {
                'params': [
                    {
                        'name': 'limit',
                        'type': 'number',
                        'required': False,
                        'min': 0,
                        'default': 20,
                        'description': 'Some human description'
                    },
                    {
                        'name': 'page',
                        'type': 'number',
                        'required': False,
                        'min': 0,
                        'default': 0,
                        'description': 'Some human description'
                    },
                ]
            },
        }
    }

    def __init__(self, *args, **kwargs):
        super(ConceptsResourceList, self).__init__(*args, **kwargs)
        self.concept_service = get_service('ConceptService')

    def get(self):
        if 'description' in request.args:
            return self.decription()

        page = long(request.args.get('page', 0))
        limit = long(request.args.get('limit', 20))

        a = datetime.datetime.now()
        concept_count = self.concept_service.count()
        concepts = [t.to_dict() for
                    t in self.concept_service.retrieve(
                        limit=limit, offset=page * limit)]
        b = datetime.datetime.now()

        response_object = {
            'meta': {
                'time': (b - a).microseconds / 1000.0,
                'count': concept_count,
                'next': self.ep_name + '?page={}&limit={}'
                .format(page + 1, limit)
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
