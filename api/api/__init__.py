import json

from flask import Flask
from flask.ext import restful
from flask import request

from objectcube.vo import Concept
from objectcube.factory import get_service

app = Flask(__name__)
api = restful.Api(app)


class ConceptsResourceList(restful.Resource):
    def __init__(self, *args, **kwargs):
        super(ConceptsResourceList, self).__init__(*args, **kwargs)
        self.concept_service = get_service('ConceptService')

    def get(self):
        limit = long(request.args.get('limit', 100))
        offset = long(request.args.get('offset', 0))
        tags = [t.to_dict() for
                t in self.concept_service.retrieve(limit=limit, offset=offset)]
        return tags

    def post(self):
        data = json.loads(request.data)
        title = data.get('title')
        description = data.get('description', '')

        if not title:
            return 'Concept must have a title', 400
        try:
            concept = self.concept_service.add(Concept(title=title,
                                                       description=description))
        except Exception as ex:
            return ex.message, 401
        return concept.to_dict(), 201

api.add_resource(ConceptsResourceList, '/concepts')


@app.route('/')
def index():
    return 'o3'

if __name__ == '__main__':
    app.run(debug=True)