import json
from datetime import datetime

from flask import request
from flask_restful import Resource

from meta import api_metable

from objectcube.data_objects import Concept
from objectcube.factory import get_service


@api_metable
class ConceptResource(Resource):
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
                        'label': 'Limit',
                        'type': 'number',
                        'required': False,
                        'min': 0,
                        'default': 20,
                        'description': 'Number of items per page',
                        },
                    {
                        'name': 'offset',
                        'label': 'Page',
                        'type': 'number',
                        'required': False,
                        'min': 0,
                        'default': 0,
                        'description': 'Page number to retrieve'
                    }
                ]
            },
            'post': {
                'params': [
                    {
                        'name': 'title',
                        'label': 'Title',
                        'type': 'string',
                        'required': True,
                        'min': 0,
                        'description': 'Title of the concept'
                    },
                    {
                        'name': 'description',
                        'label': 'Description',
                        'type': 'string',
                        'required': False,
                        'min': 0,
                        'description': 'Description of the concept'
                    }
                ]
            }
        }
    }

    def __init__(self, *args, **kwargs):
        super(ConceptResource, self).__init__(*args, **kwargs)
        self.concept_service = get_service('ConceptService')

    def get(self):
        if 'description' in request.args:
            return self.description

        page = long(request.args.get('page', 0))
        limit = long(request.args.get('limit', 20))

        a = datetime.now()
        concept_count = self.concept_service.count()
        concepts = [t.to_dict() for
                    t in self.concept_service.retrieve(
                    limit=limit, offset=page * limit)]
        b = datetime.now()

        response_object = {
            'meta': {
                'time': (b - a).microseconds / 1000.0,
                'count': concept_count,
                'next': self.ep_name + '?page={}&limit={}'
                .format(page + 1, limit)
            },
            'concepts': concepts
        }

        return response_object

    def post(self):
        data = json.loads(request.data)
        if data is None:
            return 'No data to post', 400
        title = data.get('title')
        description = data.get('description', '')

        if not title:
            return 'Concept must have a title', 400
        else:
            title = unicode(title)
        if not description:
            return 'Concept must have a description', 400
        else:
            description = unicode(description)
        try:
            concept = self.concept_service.add(
                Concept(title=title, description=description))
        except Exception as ex:
            return ex.message, 401
        return concept.to_dict(), 201


@api_metable
class ConceptResourceByID(Resource):
    ep_name = 'api/concepts/<int:id>'
    description = {
        'endpoint': ep_name,
        'title': 'ConceptByID',
        'description': 'Endpoint for fetching and updating single concepts',
        'methods': {
            'get': {
                'params': {
                    'name': 'identity',
                    'label': 'ID',
                    'type': 'number',
                    'required': True,
                    'description': 'ID of the object to fetch',
                },
            },
            'put': {
                'params': [
                    {
                        'name': 'title',
                        'label': 'Title',
                        'type': 'string',
                        'required': False,
                        'description': 'Title of the concept'
                    },
                    {
                        'name': 'description',
                        'label': 'Description',
                        'type': 'string',
                        'required': False,
                        'description': 'Description of the concept'
                    }
                ]
            },
            'delete': {
                'params': {
                    'name': 'identity',
                    'label': 'ID',
                    'type': 'number',
                    'required': True,
                    'description': 'ID of the concept to fetch',
                },
            },
        }
    }

    def __init__(self, *args, **kwargs):
        super(ConceptResourceByID, self).__init__(*args, **kwargs)
        self.concept_service = get_service('ConceptService')

    def get(self, id_):
        id_ = long(id_)
        if 'description' in request.args:
            return self.description

        a = datetime.now()
        concept = self.concept_service.retrieve_by_id(id_)
        b = datetime.now()

        if concept is None:
            return 'No concept found for ID: {}'.format(id_), 404

        response_object = {
            'meta': {
                'time': (b - a).microseconds / 1000.0
            },
            'concept': concept.to_dict()
        }

        return response_object, 200

    def put(self, id_):
        id_ = long(id_)
        if not request.data:
            return 'Missing title and/or description for edit', 400
        data = json.loads(request.data)
        title = data.get('title', '')
        description = data.get('description', '')

        if not title and not description:
            return 'Missing title and/or description for edit', 400

        concept = self.concept_service.retrieve_by_id(id_)
        if concept is None:
            return 'No concept exists with id {}'.format(id_), 404
        if title:
            concept.title = unicode(title)
        if description:
            concept.description = unicode(description)

        try:
            concept = self.concept_service.update(concept)
        except Exception as ex:
            return ex.message, 401
        return concept.to_dict(), 200

    def delete(self, id_):
        id_ = long(id_)
        try:
            self.concept_service.delete_by_id(id_)
        except Exception as ex:
            return ex.message, 404

        return 'Concept id={} deleted.'.format(id_), 204
