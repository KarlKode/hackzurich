from flask import Flask, jsonify, request, abort
from sqlalchemy.orm.exc import NoResultFound

from db import db, Recipe, Ingredient, Inventory, ShoppingList, to_json
import settings


app = Flask(__name__)
app.config.from_object(settings)
db.init_app(app)


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


@app.route('/ingredient')
def ingredient_list():
    ingredients = Ingredient.query.all()
    return jsonify(ingredients=list(map(to_json, ingredients)))


@app.route('/ingredient/<int:ean>')
def ingredient_details(ean):
    try:
        ingredient = Ingredient.query.filter_by(ean=ean).one()
    except NoResultFound:
        ingredient = Ingredient.fetch(ean)
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
        shopping_list = ShoppingList.query.order_by(ShoppingList.id.desc()).first()
    return jsonify(ingredients=list(map(to_json, shopping_list.ingredients)))


@app.route('/inventory', methods=['GET', 'POST'])
def inventory_details():
    inventory = Inventory.get_current()
    if request.method == 'POST':
        data = request.get_json(force=True)
        if not 'inventory' in data:
            abort(400)
        for item in data['inventory']:
            ingredient = Ingredient.get_by_id_or_ean(item)
            if not ingredient:
                ingredient = Ingredient.fetch(data.get('ean'))
            inventory.add_ingredient(ingredient)
        db.session.commit()
        return jsonify(inventory=inventory.to_json())
    else:
        return jsonify(inventory=inventory.to_json())


@app.route('/inventory/<id_or_ean>', methods=['DELETE'])
def inventory_delete(id_or_ean):
    inventory = Inventory.get_current()
    ingredient = Ingredient.get_by_id_or_ean({'id': id_or_ean, 'ean': id_or_ean})
    if not ingredient:
        ingredient = Ingredient.fetch(id_or_ean)
    inventory.remove_ingredient(ingredient)
    db.session.commit()


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
