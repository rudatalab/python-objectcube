from flask import Flask
from flask import jsonify
from flask import render_template
from flask.ext import restful
from resources import ConceptsResourceList

from meta import get_all_meta

app = Flask(__name__)
api = restful.Api(app)

api.add_resource(ConceptsResourceList, '/api/concepts')


@app.route('/api/description')
def api_client():
    f = get_all_meta()
    return jsonify(**f)


@app.route('/api')
def index():
    return render_template('api.html')


if __name__ == '__main__':
    app.run(debug=True)
