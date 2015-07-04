import json
from datetime import datetime

from flask import request
from flask_restful import Resource

from meta import api_metable

from objectcube.data_objects import Tag
from objectcube.factory import get_service


@api_metable
class TagResource(Resource):
    ep_name = 'api/tags'
    description = {
        'endpoint': ep_name,
        'title': 'Tags',
        'description': 'Endpoint for fetching and creating tags',
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
                        'description': 'How many results per page',
                        },
                    {
                        'name': 'offset',
                        'label': 'Page',
                        'type': 'number',
                        'required': False,
                        'min': 0,
                        'default': 0,
                        'description': 'Page number to view'
                    },
                    ]
            },
            'post': {
                'params': [
                    {
                        'name': 'value',
                        'label': 'Value',
                        'type': 'string',
                        'required': True,
                        'min': 0,
                        'description': 'Value of the Tag to create'
                    },
                    {
                        'name': 'description',
                        'label': 'Description',
                        'type': 'string',
                        'required': False,
                        'min': 0,
                        'description': 'Description of the Tag to create'
                    },
                    {
                        'name': 'type',
                        'label': 'Type',
                        'type': 'number',
                        'required': True,
                        'min': 0,
                        'description': 'Type of Tag to create'
                    }
                ]
            }
        }
    }

    def __init__(self, *args, **kwargs):
        super(TagResource, self).__init__(*args, **kwargs)
        self.tag_service = get_service('TagService')

    def get(self):
        if 'description' in request.args:
            return self.description

        page = long(request.args.get('page', 0))
        limit = long(request.args.get('limit', 20))

        a = datetime.now()
        tag_count = self.tag_service.count()
        tags = [t.to_dict() for
                t in self.tag_service.retrieve(
                limit=limit, offset=page * limit)]
        b = datetime.now()

        response_object = {
            'meta': {
                'time': (b - a).microseconds / 1000.0,
                'count': tag_count,
                'next': self.ep_name + '?page={}&limit={}'
                .format(page + 1, limit)
            },
            'tags': tags
        }

        return response_object

    def post(self):
        data = json.loads(request.data)
        if data is None:
            return 'No data to post', 400

        value = data.get('value')
        type_ = data.get('type')
        mutable = data.get('mutable')
        description = data.get('description')

        if value is None:
            return 'Tag must have a value', 400
        else:
            value = unicode(value)
        if description is None:
            return 'Tag must have a description', 400
        else:
            description = unicode(description)
        if type_ is None:
            return 'Tag must have a type', 400
        else:
            type_ = long(type_)
        if mutable is None:
            return 'Tag must have mutable value', 400
        else:
            mutable = bool(mutable)

        try:
            tag = self.tag_service.add(
                Tag(value=value,
                    description=description,
                    type=type_,
                    mutable=mutable))
        except Exception as ex:
            return ex.message, 401
        return tag.to_dict(), 201


@api_metable
class TagResourceByID(Resource):
    ep_name = 'api/tags/<int:id>'
    description = {
        'endpoint': ep_name,
        'title': 'Tags by ID',
        'description': 'Endpoint for fetching and updating single tags',
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
                        'name': 'value',
                        'label': 'Value',
                        'type': 'string',
                        'required': False,
                        'min': 0,
                        'description': 'Value of the Tag to create'
                    },
                    {
                        'name': 'description',
                        'label': 'Description',
                        'type': 'string',
                        'required': False,
                        'min': 0,
                        'description': 'Description of the Tag to create'
                    },
                    {
                        'name': 'type',
                        'label': 'Type',
                        'type': 'number',
                        'required': False,
                        'min': 0,
                        'description': 'Type of Tag to create'
                    }
                ]
            },
            'delete': {
                'params': {
                    'name': 'identity',
                    'label': 'ID',
                    'type': 'number',
                    'required': True,
                    'description': 'ID of the tag to fetch',
                    },
                }
        }
    }

    def __init__(self, *args, **kwargs):
        super(TagResourceByID, self).__init__(*args, **kwargs)
        self.tag_service = get_service('TagService')

    def get(self, id_):
        id_ = long(id_)
        if 'description' in request.args:
            return self.description

        a = datetime.now()
        tag = self.tag_service.retrieve_by_id(id_)
        b = datetime.now()

        if tag is None:
            return 'No tag found for ID: {}'.format(id_), 404

        response_object = {
            'meta': {
                'time': (b - a).microseconds / 1000.0
            },
            'tag': tag.to_dict()
        }

        return response_object, 200

    def put(self, id_):
        id_ = long(id_)
        data = json.loads(request.data)
        if data is None:
            return 'Missing value, type or description for edit', 400
        tag_value = data.get('value')
        tag_type = data.get('type')
        description = data.get('description')

        if not tag_value and not description and not tag_type:
            return 'Missing value, type or description for edit', 400

        tag = self.tag_service.retrieve_by_id(id_)
        if tag is None:
            return 'No tag exists with id {}'.format(id_), 404
        if tag_value:
            tag.value = unicode(tag_value)
        if description:
            tag.description = unicode(description)
        if tag_type:
            tag.type = long(tag_type)

        try:
            tag = self.tag_service.update(tag)
        except Exception as ex:
            return ex.message, 401
        return tag.to_dict(), 200

    def delete(self, id_):
        id_ = long(id_)
        try:
            tag = self.tag_service.retrieve_by_id(id_)
            self.tag_service.delete(tag)
        except Exception as ex:
            return ex.message, 404

        return 'Tag id={} deleted.'.format(id_), 204


@api_metable
class TagResourceByValue(Resource):
    ep_name = 'api/tags/values'
    description = {
        'endpoint': ep_name,
        'title': 'Tags by value',
        'description': 'Endpoint for fetching tags by value',
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
                        'description': 'How many results per page',
                        },
                    {
                        'name': 'offset',
                        'label': 'Page',
                        'type': 'number',
                        'required': False,
                        'min': 0,
                        'default': 0,
                        'description': 'Page number to view'
                    }
                ]
            }
        }
    }

    def __init__(self, *args, **kwargs):
        super(TagResourceByValue, self).__init__(*args, **kwargs)
        self.tag_service = get_service('TagService')

    def get(self):
        if 'description' in request.args:
            return self.description

        value = request.args.get('value')
        if not value:
            return 'Missing tag value', 400
        page = long(request.args.get('page', 0))
        limit = long(request.args.get('limit', 20))

        a = datetime.now()
        tags = [t.to_dict() for
                t in self.tag_service.retrieve_by_value(
                value=value, limit=limit, offset=page * limit)]
        b = datetime.now()

        if not tags:
            return 'No tags found for value: {}'.format(value), 404

        response_object = {
            'meta': {
                'time': (b - a).microseconds / 1000.0,
                'next': self.ep_name + '?page={}&limit={}'
                .format(page + 1, limit)
            },
            'tags': tags
        }

        return response_object, 200
