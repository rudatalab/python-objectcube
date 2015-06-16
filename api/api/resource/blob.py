from datetime import datetime
from flask.ext import restful
from flask import request
from objectcube.factory import get_service
from meta import api_metable


@api_metable
class BlobResourceByURI(restful.Resource):
    ep_name = 'api/blobs/uri/<digest>'
    description = {
        'endpoint': ep_name,
        'title': 'Blobs',
        'description': 'Endpoint for fetching and creating blobs',
        'methods': {
            'get': {
                'params': [
                    {
                        'name': 'digest',
                        'label': 'Digest',
                        'type': 'string',
                        'required': True,
                        'min': 0,
                        'default': 20,
                        'description': 'Digest to retrieve via uri'
                    }
                ]
            }
        }
    }

    def __init__(self, *args, **kwargs):
        super(BlobResourceByURI, self).__init__(*args, **kwargs)
        self.blob_service = get_service('BlobService')

    def get(self, digest):
        if 'description' in request.args:
            return self.description

        a = datetime.now()
        blob = self.blob_service.retrieve_uri(digest)
        b = datetime.now()

        response_object = {
            'meta': {
                'time': (b - a).microseconds / 1000.0,
            },
            'uri': blob
        }

        return response_object, 200
