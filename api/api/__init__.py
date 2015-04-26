from flask import Flask
from flask import render_template
from flask.ext import restful
from resources import ConceptsResourceList

app = Flask(__name__)
api = restful.Api(app)

api.add_resource(ConceptsResourceList, '/api/concepts')


@app.route('/api')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
