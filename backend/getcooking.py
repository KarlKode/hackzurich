from flask import Flask, jsonify, request
from db import db, Recipe, Ingredient, Inventory, ShoppingList
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
    i3 = Ingredient('markers', 3086120017446)
    db.session.add(i3)

    r0 = Recipe('tomato soup', 1, 30)
    db.session.add(r0)
    r0.add_ingredient(i0, '1', 'crate')
    r0.add_ingredient(i1, '1', 'cup')

    s0 = ShoppingList(r0)
    s0.add_ingredient(i3, '1', 'foo')
    db.session.add(s0)
    
    inventory0 = Inventory("user@user.com")
    db.session.add(inventory0)
    inventory0.add_ingredient(i1, '1', 'cup')
    db.session.commit()
    return 'done'


@app.route('/ingredient/<int:ean>')
def ingredient(ean):
    ingredient_obj = Ingredient.query.get_or_404(ean=ean)
    return jsonify(ingredient=ingredient_obj)


@app.route('/shopping_list', methods=['GET', 'POST'])
def shopping_list():
    if request.method == 'POST':
        sl = ShoppingList(None)
        ingredients = request.json(force=True)['ingredients']
        for ingredient_json_obj in ingredients:
            if 'id' in ingredient_json_obj:
                ingredient_obj = Ingredient.query.get_or_404(ingredient_json_obj['id'])
            else:
                ingredient_obj = Ingredient.query.get_or_404(ean=ingredient_json_obj['ean'])
            sl.add_ingredient(ingredient_obj, '1', 'foo')
        db.session.add(sl)
        db.session.commit()
    else:
        sl = ShoppingList.query.order_by(ShoppingList.id.desc()).get_or_404()
    return jsonify(items=list(map(lambda i: i.to_json(), sl.ingridients)))


@app.route('/inventory', methods=['GET','POST'])
def inventory():
    if request.method =='POST':
        return jsonify(success=True, error=None)
    else:
        inventory = Inventory.query.first().to_json()
        return jsonify(inventory=inventory)



@app.route('/recipes')
def recipes():
    inventory = Inventory.query.first().to_json()
    recipe_list = list(map(lambda o: o.to_json(inventory), Recipe.query.all()))
    print(Recipe.query.all())
    return jsonify(recipes=recipe_list)


@app.route('/recipe/<int:recipe_id>')
def recipe(recipe_id):
    inventory = Inventory.query.first().to_json()
    recipe_obj = Recipe.query.get_or_404(recipe_id)
    return jsonify(recipe=recipe_obj.to_json(inventory))



if __name__ == '__main__':
    app.run()
