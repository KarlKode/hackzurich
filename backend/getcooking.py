import logging
from flask import Flask, jsonify, request, abort
from flask.ext import admin
from flask.ext.admin.contrib import sqla
from flask.ext.admin.contrib.sqla.ajax import QueryAjaxModelLoader
import requests
from sqlalchemy.orm import joinedload
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
    sl = ShoppingList()
    sl.user = 'marc@marcg.ch'
    db.session.add(sl)

    inv = Inventory()
    inv.user = 'marc@marcg.ch'
    db.session.add(inv)

    db.session.commit()
    return 'done'


@app.route('/load')
def load():
    # Get total hits
    base_url = url = 'https://test-web-api.migros.ch/eth-hack/products?key=k0DFQajkP8AnGMF9&limit=%d&offset=%d'
    r = requests.get(base_url % (0, 0))
    data = r.json()
    if not 'total_hits' in data:
        abort(500)
    total = int(data['total_hits'])
    inserted = 0
    while inserted < total:
        r = requests.get(base_url % (100, inserted))
        data = r.json()
        if not 'products' in data:
            abort(500)
        products = data['products'].values()
        for product in products:
            eans = product['eans']
            ingredient = Ingredient()
            db.session.add(ingredient)
            ingredient.title = product['name']
            for ean_code in eans:
                ingredient.add_ean(ean_code)
            ingredient.from_product(product)
            inserted += 1
        db.session.commit()
    return jsonify(success=True, imported=inserted)


@app.route('/ingredient')
def ingredient_list():
    query = db.session.query(Ingredient).options(joinedload(Ingredient.eans))
    if 'q' in request.args:
        query = query.filter(Ingredient.title.like('%%%s%%' % request.args.get('q')))
    if 'limit' in request.args:
        query = query.limit(int(request.args.get('limit')))
    else:
        query = query.limit(10)
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


def delete_shoppinglist():
    data = request.get_json(force=True)
    if not 'ingredients' in data:
        abort(400)
    eans = []
    ids_remove = []
    for item in data['ingredients']:
        if 'id' in item:
            ids_remove.append(item['id'])
        else:
            eans.append(item['ean'])
    ids = db.session.query(EAN.ingredient_id).filter(EAN.ean.in_(eans)).all()
    ids = [id[0] for id in ids] + ids_remove
    db.session.query(ShoppingListIngredients).filter(
        ShoppingListIngredients.ingredient_id.in_(ids_remove)).delete(
        synchronize_session='fetch')
    db.session.commit()
    return jsonify(ok=True)


@app.route('/shopping_list/delete', methods=['POST'])
def shopping_list_del():
    return delete_shoppinglist()

@app.route('/shopping_list', methods=['GET', 'POST', 'DELETE'])
def shopping_list_details():
    if request.method == 'DELETE':
        return delete_shoppinglist()
    elif request.method == 'POST':
        shopping_list = ShoppingList.query.first()
        data = request.get_json(force=True)
        if not 'ingredients' in data:
            abort(400)
        for item in data['ingredients']:
            ingredient = Ingredient.get_by_id_or_ean(item)
            shopping_list.add_ingredient(ingredient, item.get('amount'), item.get('unit'))
        db.session.commit()
        return jsonify(ok=True)
    else:
        shopping_list = db.session.query(ShoppingList).options(joinedload(*ShoppingList.ingredients.attr)).order_by(ShoppingList.id.desc()).first()
        print shopping_list.ingredients
    return jsonify(ingredients=list(i.to_json()  for i in shopping_list.ingredients if i))


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
                continue
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
        ids_remove = []
        for item in data['inventory']:
            if 'id' in item:
                ids_remove.append(item['id'])
            else:
                eans.append(item['ean'])
        ids = db.session.query(EAN.ingredient_id).filter(EAN.ean.in_(eans)).all()
        ids = [id[0] for id in ids] + ids_remove
        db.session.query(InventoryIngredients).filter(InventoryIngredients.ingredient_id.in_(ids_remove)).delete(
            synchronize_session='fetch') 
        db.session.commit()
        return jsonify(ok=True)


@app.route('/inventory/<id_or_ean>', methods=['DELETE'])
def inventory_delete(id_or_ean):
    inventory = Inventory.get_current()
    ingredient = Ingredient.get_by_id_or_ean({'id': id_or_ean, 'ean': id_or_ean})
    if not ingredient:
        return
    inventory.remove_ingredient(ingredient)
    db.session.commit()


def current_inventory():
    return db.session.query(Inventory).options(joinedload(*Inventory.ingredients.attr)).first().to_json()


@app.route('/recipe', methods=['GET'])
def recipe_list():
    inventory = current_inventory()
    if not inventory:
        abort(400)
    recipes = db.session.query(Recipe).options(joinedload(*Recipe.ingredients.attr)).options(joinedload(Recipe.steps))
    recipes = list(o.to_json_small(inventory) for o in recipes.all())
    return jsonify(recipes=sorted(recipes, key=lambda x: x['missing']))


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
    inventory = current_inventory()
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
    logging.basicConfig()
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    app.run(threaded=True)
