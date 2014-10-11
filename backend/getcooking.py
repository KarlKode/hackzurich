import random
from flask import Flask, jsonify, request, abort
from flask.ext.cors import CORS
import requests
from sqlalchemy.orm.exc import NoResultFound

from db import db, Recipe, Ingredient, Inventory, ShoppingList, to_json, \
    RecipeIngredients, Step, InventoryIngredients, ShoppingListIngredients
import settings


app = Flask(__name__)
cors = CORS(app,automatic_options=True, headers=['Content-Type','X-DevTools-Emulate-Network-Conditions-Client-Id'])
app.config.from_object(settings)
db.init_app(app)


@app.route('/')
def hello_world():
    return 'GET /shopping_list<br>POST /inventory<br>GET /recipes'


@app.route('/install')
def install():
    db.drop_all()
    db.create_all()
    ingredients = []
    for i in range(0,20):
        i0 = Ingredient('tomato'+str(i), i)
        db.session.add(i0)
        ingredients.append(i0)
    i3 = Ingredient('markers', 3086120017446)
    db.session.add(i3)
    ingredients.append(i3)

    for i in range(0,100):
        r0 = Recipe('tomato soup', 1, 30)
        db.session.add(r0)
        ingr=set([])
        for i in range(0,6):
            ingr.add(random.choice(ingredients))
        for i in range(0,int(random.uniform(4,8))):
            s = Step()
            s.recipe = r0
            s.title = "Step"+str(i)
            s.description = "Lorem ipsum orem ipsum orem ipsumorem ipsumorem ipsumorem ipsumorem ipsum"+str(i)
            db.session.add(s)
        for i in ingr:
            r0.add_ingredient(i, random.uniform(1,2000), 'g')

    s0 = ShoppingList()
    s0.add_ingredient(i3, '1', 'foo')
    db.session.add(s0)

    inventory0 = Inventory("user@user.com")
    db.session.add(inventory0)
    ingr=set([])
    for i in range(0,6):
        ingr.add(random.choice(ingredients))
    for i in ingr:
        inventory0.add_ingredient(i, random.uniform(1,2000), 'g')
    db.session.commit()
    return 'done'

@app.route('/load')
def load():
    last_empty = False
    offset=0
    while not last_empty:
        url = 'https://test-web-api.migros.ch/eth-hack/products?key=k0DFQajkP8AnGMF9&limit=%s' % str(12)
        offset +=12
        print url
        r = requests.get(url)
        data = r.json()
        for k,v in data['products'].items():
            print v['receipt_text']
            print v['eans']
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


@app.route('/shopping_list', methods=['GET', 'POST', 'DELETE'])
def shopping_list_details():
    if request.method == 'DELETE':
        data = request.get_json(force=True)
        if not 'ingredients' in data:
            abort(400)
        eans = []
        for item in data['ingredients']:
            eans.append(item['ean'])
        ids =  db.session.query(ShoppingListIngredients.id)\
            .join(ShoppingListIngredients.ingredient)\
            .filter(Ingredient.ean.in_(eans)).all()
        ids = [id[0] for id in ids]
        db.session.query(ShoppingListIngredients).filter(ShoppingListIngredients.id.in_(ids)).delete(synchronize_session='fetch')
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
        ids =  db.session.query(InventoryIngredients.id)\
            .join(InventoryIngredients.ingredient)\
            .filter(Ingredient.ean.in_(eans)).all()
        ids = [id[0] for id in ids]
        db.session.query(InventoryIngredients).filter(InventoryIngredients.id.in_(ids)).delete(synchronize_session='fetch')
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


@app.route('/recipe')
def recipe_list():
    inventory = Inventory.query.first().to_json()
    recipes = db.session.query(Recipe).join(Recipe.recipe_ingredients).join(RecipeIngredients.ingredient)
    recipe_list = list(o.to_json_small(inventory) for o in recipes.all())
    return jsonify(recipes=sorted(recipe_list,key=lambda x:x['missing']))



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

@app.after_request
def close_connection(response):
    db.session.close()
    return response

if __name__ == '__main__':
    app.run(threaded=True)
