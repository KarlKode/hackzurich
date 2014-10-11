from flask import Flask, jsonify, request, abort
import requests
from sqlalchemy.orm.exc import NoResultFound
from db import db, Recipe, Ingredient, Inventory, ShoppingList
import settings

app = Flask(__name__)
app.config.from_object(settings)
db.init_app(app)


def to_json(obj):
    return obj.to_json()


@app.route('/')
def hello_world():
    return 'GET /shopping_list<br>POST /inventory<br>GET /recipes'


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
    i3 = Ingredient('markers', 3086120017446)
    db.session.add(i3)

    r0 = Recipe('tomato soup', 1, 30)
    db.session.add(r0)
    r0.add_ingredient(i0)
    r0.add_ingredient(i1)

    s0 = ShoppingList()
    s0.add_ingredient(i3)
    db.session.add(s0)
    
    inventory0 = Inventory()
    db.session.add(inventory0)
    inventory0.add_ingredient(i1)
    db.session.commit()
    return 'done'


@app.route('/ingredient/<int:ean>')
def ingredient_details(ean):
    try:
        ingredient = Ingredient.query.filter_by(ean=ean).one()
    except NoResultFound:
        r = requests.get('http://api.autoidlabs.ch/products/%s?n=1' % ean)
        data = r.json()
        if not 'name' in data:
            abort(404)
        ingredient = Ingredient(data['name'], ean, data['image']['original'])
        db.session.add(ingredient)
        db.session.commit()
    return jsonify(ingredient=ingredient.to_json())


@app.route('/shopping_list', methods=['GET', 'POST'])
def shopping_list_details():
    if request.method == 'POST':
        shopping_list = ShoppingList()
        db.session.add(shopping_list)
        data = request.get_json(force=True)
        if not 'ingredients' in data:
            abort(400)
        for item in data['ingredients']:
            ingredient = Ingredient.get_by_id_or_ean(item)
            shopping_list.add_ingredient(ingredient)
        db.session.commit()
    else:
        shopping_list = ShoppingList.query.order_by(ShoppingList.id.desc()).get_or_404()
    return jsonify(items=list(map(lambda i: i.to_json(), shopping_list.ingridients)))


@app.route('/inventory', methods=['GET', 'POST', 'DELETE'])
def inventory_details():
    inventory = Inventory.query.first()
    if request.method == 'POST':
        data = request.get_json(force=True)
        if not 'inventory' in data:
            abort(400)
        for item in data['inventory']:
            ingredient = Ingredient.get_by_id_or_ean(item)
            if not ingredient:
                # TODO: get inventory data from API
                ingredient = None
            inventory.add_ingredient(ingredient)
        db.session.commit()
        return jsonify(inventory=inventory.to_json())
    elif request.method == 'DELETE':
        data = request.get_json(force=True)
        if not 'inventory' in data:
            abort(400)
        for item in data['inventory']:
            ingredient = Ingredient.get_by_id_or_ean(item)
            if not ingredient:
                # TODO: get inventory data from API
                ingredient = None
            inventory.remove_ingredient(ingredient)
    else:
        return jsonify(inventory=inventory.to_json())


@app.route('/recipe')
def recipe_list():
    recipes = Recipe.query.all()
    return jsonify(recipes=list(map(to_json, recipes)))


@app.route('/recipe/best')
def recipe_best_list():
    recipes = Recipe.query.all()
    # TODO: Select best recipes
    return jsonify(recipes=list(map(to_json, recipes)))


@app.route('/recipe/<int:recipe_id>')
def recipe_details(recipe_id):
    inventory = Inventory.query.first().to_json()
    recipe = Recipe.query.get_or_404(recipe_id)
    return jsonify(recipe=recipe.to_json(inventory))


if __name__ == '__main__':
    app.run()
