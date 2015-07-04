from flask import Flask, jsonify, render_template
from flask_restful import Api

from resource.concept import ConceptResource, ConceptResourceByID
from resource.tag import TagResource, TagResourceByID, TagResourceByValue
from resource.object import ObjectResource, ObjectResourceByID
from resource.blob import BlobResourceByURI
from resource.meta import get_all_meta

app = Flask(__name__)
api = Api(app)

# Concept API
api.add_resource(ConceptResource, '/api/concepts')
api.add_resource(ConceptResourceByID, '/api/concepts/<int:id_>')

# Tag API
api.add_resource(TagResource, '/api/tags')
api.add_resource(TagResourceByID, '/api/tags/<int:id_>')
api.add_resource(TagResourceByValue, '/api/tags/values')

# Object API
api.add_resource(ObjectResource, '/api/objects')
api.add_resource(ObjectResourceByID, '/api/objects/<int:id_>')

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
