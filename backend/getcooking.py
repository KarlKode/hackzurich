from flask import Flask, jsonify
from db import db, Recipe, Ingredient
import settings

app = Flask(__name__)
app.config.from_object(settings)
db.init_app(app)


@app.route('/')
def hello_world():
    return 'GET /shopping_list\nPOST /inventory\nGET /recipes\n'


@app.route('/install')
def install():
    db.drop_all()
    db.create_all()
    i0 = Ingredient('tomato', 123)
    db.session.add(i0)
    i1 = Ingredient('onion', 124)
    db.session.add(i1)
    i2 = Ingredient('creme', 111)
    db.session.add(i2)

    r0 = Recipe('tomato soup', 1, 30)
    db.session.add(r0)
    r0.add_ingredient(i0, '1', 'crate')
    r0.add_ingredient(i1, '1', 'cup')
    db.session.commit()
    return 'done'

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
    recipe_list = list(map(lambda o: o.to_json(), Recipe.query.all()))
    print(Recipe.query.all())
    return jsonify(recipes=recipe_list)


@app.route('/recipe/<int:recipe_id>')
def recipe(recipe_id):
    recipe_obj = Recipe.query.get_or_404(recipe_id)
    return jsonify(recipe=recipe_obj.to_json())



if __name__ == '__main__':
    app.run()
