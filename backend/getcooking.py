from flask import Flask, jsonify
import settings

app = Flask(__name__)
app.config.from_object(settings)


@app.route('/')
def hello_world():
    return 'GET /shopping_list\nPOST /inventory\nGET /recipes\n'


@app.route('/shopping_list')
def shopping_list():
    l = [
        {'id': 1, 'name': 'tomato', 'ean': 123},
        {'id': 2, 'name': 'cucumber', 'ean': 124},
        {'id': 3, 'name': 'onion', 'ean': 12345},
    ]
    return jsonify(items=l)


@app.route('/inventory', methods=['POST'])
def inventory():
    return jsonify(success=True, error=None)


@app.route('/recipes')
def recipes():
    recipe_list = [
        {
            'id': 1,
            'title': 'tomato soup',
            'images': ['/static/images/tomato_soup-1.png', '/static/images/tomato_soup-2.png', ],
            'ingredients': [
                {
                    'id': 1,
                    'title': 'tomato',
                    'ean': 123,
                    'image': None,
                    'amount': 2,
                    'unit': 'kg',
                },
                {
                    'id': 3,
                    'title': 'onion',
                    'ean': 12345,
                    'image': None,
                    'amount': 10,
                    'unit': 'pieces',
                },
            ],
            'steps': [
                {
                    'id': 1,
                    'title': 'cook the stuff',
                    'description': 'Just put it in a pan',
                    'image': '/static/images/step/tomato_soup-1.png',
                },
                {
                    'id': 2,
                    'title': 'serve',
                    'description': 'Just put in on a plate',
                    'image': '/static/images/step/tomato_soup-2.png',
                }
            ],
            'duration': 45,
            'difficulty': 1,
        },
        {
            'id': 2,
            'title': 'tomato soup 2',
            'images': ['/static/images/tomato_soup-3.png', '/static/images/tomato_soup-4.png', ],
            'ingredients': [
                {
                    'id': 1,
                    'title': 'tomato',
                    'ean': 123,
                    'image': None,
                    'amount': 1,
                    'unit': 'kg',
                },
                {
                    'id': 3,
                    'title': 'onion',
                    'ean': 12345,
                    'image': None,
                    'amount': 1,
                    'unit': 'crate',
                },
            ],
            'steps': [
                {
                    'id': 1,
                    'title': 'cook the stuff again',
                    'description': 'Just put it in a pan... Again...',
                    'image': '/static/images/step/tomato_soup-3.png',
                },
                {
                    'id': 2,
                    'title': 'serve',
                    'description': 'Just put in on a plate',
                    'image': '/static/images/step/tomato_soup-2.png',
                }
            ],
            'duration': 45,
            'difficulty': 1,
        },
    ]
    return jsonify(recipes=recipe_list)


if __name__ == '__main__':
    app.run()
