import json
from datetime import datetime
from flask.ext import restful
from flask import request
from objectcube.data_objects import Object
from objectcube.utils import md5_from_value
from objectcube.factory import get_service
from meta import api_metable


@api_metable
class ObjectResource(restful.Resource):
    ep_name = 'api/objects'

    description = {
        'endpoint': ep_name,
        'title': 'Objects',
        'description': 'Endpoint for fetching and creating objects',
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
                        'name': 'name',
                        'label': 'Name',
                        'type': 'string',
                        'required': True,
                        'description': 'Name of the object'
                    },
                    {
                        'name': 'digest',
                        'label': 'Digest',
                        'type': 'string',
                        'required': False,
                        'description': 'Digest for the object'
                    }
                ]
            }
        }
    }

    def __init__(self, *args, **kwargs):
        super(ObjectResource, self).__init__(*args, **kwargs)
        self.object_service = get_service('ObjectService')

    def get(self):
        if 'description' in request.args:
            return self.description

        page = long(request.args.get('page', 0))
        limit = long(request.args.get('limit', 20))

        a = datetime.now()
        object_count = self.object_service.count()
        objects = [o.to_dict() for o in self.object_service.retrieve(
            limit=limit, offset=page * limit)]
        b = datetime.now()

        response_object = {
            'meta': {
                'time': (b - a).microseconds / 1000.0,
                'count': object_count,
                'next': self.ep_name + '?page={}&limit={}'
                .format(page + 1, limit)
            },
            'objects': objects
        }

        return response_object

    def post(self):
        data = json.loads(request.data)
        if data is None:
            return 'No data to post', 400
        name = data.get('name')
        digest = data.get('digest')

        if name is None:
            return 'Object must have a name', 400

        if digest is None:
            digest = md5_from_value(name)
        try:
            obj = self.object_service.add(Object(name=name, digest=digest))
        except Exception as ex:
            return ex.message, 401
        return obj.to_dict(), 201


@api_metable
class ObjectResourceByID(restful.Resource):
    ep_name = 'api/objects/<int:id>'

    description = {
        'endpoint': ep_name,
        'title': 'Objects by ID',
        'description': 'Endpoint for fetching and updating single objects',
        'methods': {
            'get': {
                'params': {
                    'name': 'identity',
                    'label': 'ID',
                    'type': 'number',
                    'required': True,
                    'description': 'ID of the object to fetch',
                    }
            },
            'put': {
                'params': [
                    {
                        'name': 'name',
                        'label': 'Name',
                        'type': 'string',
                        'required': False,
                        'min': 0,
                        'description': 'Name of the object'
                    },
                    {
                        'name': 'digest',
                        'label': 'Digest',
                        'type': 'string',
                        'required': False,
                        'min': 0,
                        'description': 'Digest for the object'
                    }
                ]
            },
            'delete': {
                'params': {
                    'name': 'identity',
                    'label': 'ID',
                    'type': 'number',
                    'required': True,
                    'description': 'ID of the object to fetch',
                    },
                }
        }
    }

    def __init__(self, *args, **kwargs):
        super(ObjectResourceByID, self).__init__(*args, **kwargs)
        self.object_service = get_service('ObjectService')

    def get(self, _id):
        if 'description' in request.args:
            return self.description

        a = datetime.now()
        obj = self.object_service.retrieve_by_id(_id)
        b = datetime.now()

        if obj is None:
            return 'No tag found for ID: {}'.format(_id), 404

        response_object = {
            'meta': {
                'time': (b - a).microseconds / 1000.0
            },
            'object': obj.to_dict()
        }

        return response_object, 200

    def put(self, _id):
        data = json.loads(request.data)
        if data is None:
            return 'Missing name and/or digest for edit', 400
        obj_name = data.get('name')

        if not obj_name:
            return 'Missing name and/or digest for edit', 400

        obj = self.object_service.retrieve_by_id(_id)
        if obj is None:
            return 'No object exists with id {}'.format(_id), 404
        obj.name = obj_name

        try:
            obj = self.object_service.update(obj)
        except Exception as ex:
            return ex.message, 401
        return obj.to_dict(), 200

    def delete(self, _id):
        try:
            obj = self.object_service.retrieve_by_id(_id)
            self.object_service.delete(obj)
        except Exception as ex:
            return ex.message, 404

        return 'Object named {} deleted.'.format(_id), 204
