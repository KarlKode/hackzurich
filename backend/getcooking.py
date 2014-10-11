from flask import Flask, jsonify, request, abort
from flask.ext import admin
from flask.ext.admin.contrib import sqla
from flask.ext.admin.contrib.sqla.ajax import QueryAjaxModelLoader
import requests
from sqlalchemy.orm.exc import NoResultFound

from flask.ext.cors import CORS
from db import db, Recipe, Ingredient, Inventory, ShoppingList, to_json, \
    RecipeIngredients, Step, InventoryIngredients, ShoppingListIngredients, EAN
import settings


app = Flask(__name__)
cors = CORS(app, automatic_options=True, headers=['Content-Type', 'X-DevTools-Emulate-Network-Conditions-Client-Id'])
app.config.from_object(settings)
db.init_app(app)


@app.route('/')
def hello_world():
    return 'GET /shopping_list<br>POST /inventory<br>GET /recipes'


@app.route('/installaaaaaaaa')
def install():
    db.drop_all()
    db.create_all()
    return 'done'


@app.route('/load')
def load():
    ingredients = []
    # Get total hits
    base_url = url = 'https://test-web-api.migros.ch/eth-hack/products?key=k0DFQajkP8AnGMF9&limit=%d&offset=%d'
    r = requests.get(base_url % (0, 0))
    data = r.json()
    if not 'total_hits' in data:
        abort(500)
    total = int(data['total_hits'])
    while len(ingredients) < total:
        r = requests.get(base_url % (100, len(ingredients)))
        data = r.json()
        if not 'products' in data:
            abort(500)
        products = data['products'].values()
        for product in products:
            eans = product['eans']
            # Is one of the products ean codes already in the database?
            ean = None
            for ean_code in eans:
                ean = EAN.query.get(ean_code)
                if ean:
                    break
            if ean:
                ingredient = ean.ingredient
                for ean_code in eans:
                    ingredient.add_ean(ean_code)
            else:
                ingredient = Ingredient(product['name'], eans)
                db.session.add(ingredient)
            ingredient.from_product(product)
            ingredients.append(ingredient)
    db.session.commit()
    return jsonify(success=True, imported=len(ingredients))


@app.route('/ingredient')
def ingredient_list():
    query = Ingredient.query
    if 'q' in request.args:
        query = query.filter(Ingredient.title.like('%%%s%%' % request.args.get('q')))
    if 'limit' in request.args:
        query = query.limit(int(request.args.get('limit')))
    if 'offset' in request.args:
        query = query.offset(int(request.args.get('offset')))
    ingredients = query.all()
    return jsonify(ingredients=list(map(to_json, ingredients)))


@app.route('/ingredient/<int:ean>')
def ingredient_details(ean):
    try:
        ean_obj = EAN.query.filter_by(ean=ean).one()
        ingredient = ean_obj.ingredient
    except NoResultFound:
        ingredient = Ingredient.fetch(ean)
        db.session.commit()
    return jsonify(ingredient=ingredient.to_json())


@app.route('/shopping_list', methods=['GET', 'POST', 'DELETE'])
def shopping_list_details():
    if request.method == 'DELETE':
        data = request.get_json(force=True)
        if not 'ingredients' in data:
            abort(400)
        eans = []
        for item in data['ingredients']:
            eans.append(item['ean'])
        ids = db.session.query(ShoppingListIngredients.id) \
            .join(ShoppingListIngredients.ingredient) \
            .filter(Ingredient.ean.in_(eans)).all()
        ids = [id[0] for id in ids]
        db.session.query(ShoppingListIngredients).filter(ShoppingListIngredients.id.in_(ids)).delete(
            synchronize_session='fetch')
        db.session.commit()
        return jsonify(ok=True)
    elif request.method == 'POST':
        shopping_list = ShoppingList.query.first()
        db.session.add(shopping_list)
        data = request.get_json(force=True)
        if not 'ingredients' in data:
            abort(400)
        for item in data['ingredients']:
            ingredient = Ingredient.get_by_id_or_ean(item)
            shopping_list.add_ingredient(ingredient, item['amount'], item['unit'])
        db.session.commit()
    else:
        shopping_list = ShoppingList.query.order_by(ShoppingList.id.desc()).first()
    return jsonify(ingredients=list(map(to_json, shopping_list.ingredients)))


@app.route('/inventory', methods=['GET', 'POST', 'DELETE'])
def inventory_details():
    inventory = Inventory.get_current()
    if request.method == 'POST':
        data = request.get_json(force=True)
        if not 'inventory' in data:
            abort(400)
        for item in data['inventory']:
            ingredient = Ingredient.get_by_id_or_ean(item)
            if not ingredient:
                ingredient = Ingredient.fetch(item['ean'])
            inventory.add_ingredient(ingredient, None, None)
        db.session.commit()
        return jsonify(inventory=inventory.to_json())
    elif request.method == 'GET':
        return jsonify(inventory=inventory.to_json())
    elif request.method == 'DELETE':
        data = request.get_json(force=True)
        if not 'inventory' in data:
            abort(400)
        eans = []
        for item in data['inventory']:
            eans.append(item['ean'])
        ids = db.session.query(InventoryIngredients.id) \
            .join(InventoryIngredients.ingredient) \
            .filter(Ingredient.ean.in_(eans)).all()
        ids = [id[0] for id in ids]
        db.session.query(InventoryIngredients).filter(InventoryIngredients.id.in_(ids)).delete(
            synchronize_session='fetch')
        db.session.commit()
        return jsonify(ok=True)


@app.route('/inventory/<id_or_ean>', methods=['DELETE'])
def inventory_delete(id_or_ean):
    inventory = Inventory.get_current()
    ingredient = Ingredient.get_by_id_or_ean({'id': id_or_ean, 'ean': id_or_ean})
    if not ingredient:
        ingredient = Ingredient.fetch(id_or_ean)
    inventory.remove_ingredient(ingredient)
    db.session.commit()


@app.route('/recipe', methods=['GET'])
def recipe_list():
    inventory = Inventory.query.first().to_json()
    recipes = db.session.query(Recipe).join(Recipe.recipe_ingredients).join(RecipeIngredients.ingredient)
    recipe_list = list(o.to_json_small(inventory) for o in recipes.all())
    return jsonify(recipes=sorted(recipe_list, key=lambda x: x['missing']))


@app.route('/recipe', methods=['POST'])
def recipe_add():
    data = request.get_json(force=True)
    required_fields = ['title', 'images', 'difficulty', 'duration', 'steps']
    for required_field in required_fields:
        if not required_field in data:
            abort(400)
    recipe = Recipe(data['title'], data['difficulty'], data['duration'], data['images'], data['steps'])
    db.session.add(recipe)
    db.session.commit()


@app.route('/recipe/best')
def recipe_best_list():
    recipes = Recipe.query.all()
    # TODO: Select best recipes
    return jsonify(recipes=list(map(to_json, recipes)))


@app.route('/recipe/<int:recipe_id>', methods=['GET', 'DELETE'])
def recipe_details(recipe_id):
    inventory = Inventory.query.first().to_json()
    recipe = Recipe.query.get_or_404(recipe_id)
    return jsonify(recipe=recipe.to_json(inventory))


@app.after_request
def close_connection(response):
    db.session.close()
    return response


# Admin stuff
class IngredientAdmin(sqla.ModelView):
    column_searchable_list = ('title', Ingredient.title)

admin = admin.Admin(app, 'Recipe')
admin.add_view(sqla.ModelView(Recipe, db.session))
admin.add_view(sqla.ModelView(EAN, db.session))
admin.add_view(IngredientAdmin(Ingredient, db.session))
admin.add_view(sqla.ModelView(Step, db.session))
admin.add_view(sqla.ModelView(ShoppingList, db.session))
admin.add_view(sqla.ModelView(Inventory, db.session))


class RecipeIngredientsAdmin(sqla.ModelView):
    form_ajax_refs = {
        'ingredient_id': QueryAjaxModelLoader('ingredient', db.session, Ingredient, fields=['title'], page_size=10),
    }


class ShoppingListIngredientsAdmin(sqla.ModelView):
    form_ajax_refs = {
        'ingredient_id': QueryAjaxModelLoader('ingredient', db.session, Ingredient, fields=['title'], page_size=10),
    }


class InventoryIngredientsAdmin(sqla.ModelView):
    form_ajax_refs = {
        'ingredient_id': QueryAjaxModelLoader('ingredient', db.session, Ingredient, fields=['title'], page_size=10),
    }


admin.add_view(RecipeIngredientsAdmin(RecipeIngredients, db.session))
admin.add_view(ShoppingListIngredientsAdmin(ShoppingListIngredients, db.session))
admin.add_view(InventoryIngredientsAdmin(InventoryIngredients, db.session))


if __name__ == '__main__':
    app.run(threaded=True)
