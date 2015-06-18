from flask import Flask
from flask import jsonify
from flask import render_template
from flask.ext import restful

from resource.concept import ConceptResource, ConceptResourceByID
from resource.tag import TagResource, TagResourceByID, TagResourceByValue
from resource.object import ObjectResource, ObjectResourceByID
from resource.blob import BlobResourceByURI
from resource.meta import get_all_meta

app = Flask(__name__)
api = restful.Api(app)

# Concept API
api.add_resource(ConceptResource, '/api/concepts')
api.add_resource(ConceptResourceByID, '/api/concepts/<int:_id>')

# Tag API
api.add_resource(TagResource, '/api/tags')
api.add_resource(TagResourceByID, '/api/tags/<int:_id>')
api.add_resource(TagResourceByValue, '/api/tags/values')

# Object API
api.add_resource(ObjectResource, '/api/objects')
api.add_resource(ObjectResourceByID, '/api/objects/<int:_id>')

# Blob API
api.add_resource(BlobResourceByURI, '/api/blobs/uri/<string:digest>')


@app.route('/api/description')
def api_client():
    f = get_all_meta()
    return jsonify(**f)


@app.route('/api')
def index():
    return render_template('api.html')


if __name__ == '__main__':
    app.run(debug=True, port=4000)
