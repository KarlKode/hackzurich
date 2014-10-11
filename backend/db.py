import json
from flask import abort
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.ext.associationproxy import association_proxy
import requests
from sqlalchemy.orm.exc import NoResultFound

db = SQLAlchemy()


class RecipeIngredients(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'))
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredient.id'))
    amount = db.Column(db.String(500))
    unit = db.Column(db.String(500))

    recipe = db.relationship('Recipe', backref=db.backref('recipe_ingredients', lazy='joined'), lazy='joined')
    ingredient = db.relationship('Ingredient', backref=db.backref('recipe_ingredients', lazy='joined'), lazy='joined')

    def __init__(self, recipe=None, ingredient=None, amount=None, unit=None):
        if not recipe:
            return
        self.recipe = recipe
        self.ingredient = ingredient
        self.amount = amount
        self.unit = unit

    def __repr__(self):
        return '<RecipeIngredients %r>' % self.id


class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500))
    images = db.Column(db.Text)
    difficulty = db.Column(db.Integer)
    duration = db.Column(db.Integer)

    ingredients = association_proxy('recipe_ingredients', 'ingredient')

    def __init__(self, title=None, difficulty=None, duration=None, images=None, steps=None):
        if not title:
            return
        self.title = title
        self.difficulty = difficulty
        self.duration = duration
        self.images = images
        for step_data in steps or []:
            # Don't add empty steps
            if not 'title' in step_data:
                continue
            step = Step(step_data.get('title'), step_data.get('description'), step_data.get('image'), self)
            db.session.add(step)

    def __str__(self):
        return "Recipe '%s'" % self.title

    def __repr__(self):
        return '<Recipe %r>' % self.id

    def add_ingredient(self, ingredient, amount, unit):
        recipe_ingredients = RecipeIngredients(self, ingredient, amount, unit)
        db.session.add(recipe_ingredients)

    def to_json(self, inventory=None):
        ingredients = list(map(to_json, self.ingredients or []))
        return {
            'id': self.id,
            'title': self.title,
            'images': self.images,
            'difficulty': self.difficulty,
            'duration': self.duration,
            'ingredients': ingredients,
            'missing': sum(1 for i in ingredients if 'missing' in i and i['missing']),
            'steps': list(map(to_json, self.steps or []))
        }

    def to_json_small(self, inventory=None):
        ingredients = list(map(to_json, self.ingredients or []))
        return {
            'id': self.id,
            'title': self.title,
            'images': self.images,
            'difficulty': self.difficulty,
            'duration': self.duration,
            'ingredients': ingredients,
            'missing': sum(1 for i in ingredients if 'missing' in i and i['missing'])
        }


class ShoppingListIngredients(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    shopping_list_id = db.Column(db.Integer, db.ForeignKey('shopping_list.id'))
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredient.id'))
    amount = db.Column(db.String(500))
    unit = db.Column(db.String(500))

    shopping_list = db.relationship('ShoppingList', backref=db.backref('shopping_list_ingredients', lazy='joined'),
                                    lazy='joined')
    ingredient = db.relationship('Ingredient', backref=db.backref('shopping_list_ingredients', lazy='joined'),
                                 lazy='joined')

    def __init__(self, shopping_list=None, ingredient=None, amount=None, unit=None):
        self.shopping_list = shopping_list
        self.ingredient = ingredient
        self.amount = amount
        self.unit = unit

    def __repr__(self):
        return '<ShoppingListIngredients %r>' % self.id


class InventoryIngredients(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventory.id'))
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredient.id'))
    amount = db.Column(db.String(500))
    unit = db.Column(db.String(500))

    inventory = db.relationship('Inventory', backref=db.backref('inventory_ingredients', lazy='joined'), lazy='joined')
    ingredient = db.relationship('Ingredient', backref=db.backref('inventory_ingredients', lazy='joined'), lazy='joined')

    def __init__(self, inventory=None, ingredient=None, amount=None, unit=None):
        if not inventory:
            return
        self.inventory = inventory
        self.ingredient = ingredient
        self.amount = amount
        self.unit = unit

    def __repr__(self):
        return '<InventoryIngredients %r>' % self.id


class EAN(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ean = db.Column(db.BigInteger)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredient.id'))

    ingredient = db.relationship('Ingredient', backref=db.backref('eans', lazy='joined'), lazy='joined')

    def __init__(self, ean=None, ingredient=None):
        if not self.ean:
            return
        self.ean = ean
        self.ingredient = ingredient

    def __repr__(self):
        return '<EAN %d>' % self.id

    def __str__(self):
        return 'EAN: %d' % self.ean

    def to_json(self):
        return {
            'id': self.id,
            'ean': self.ean,
            'ingredient_id': self.ingredient_id,
        }


class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), index=True)
    image = db.Column(db.String(500))
    description = db.Column(db.Text)
    price = db.Column(db.Integer)
    receipt_text = db.Column(db.String(500))
    data = db.Column(db.Text)

    shopping_lists = association_proxy('shopping_list_ingredients', 'shopping_list')
    inventories = association_proxy('inventory_ingredients', 'inventory')

    def __str__(self):
        return self.title

    def __repr__(self):
        return '<Ingredient %r>' % self.id

    def to_json(self, inventory=None):
        if self.eans:
            eans = list(map(to_json, self.eans))
        else:
            eans = []
        data = {
            'id': self.id,
            'title': self.title,
            'eans': eans,
            'image': self.image,
            'description': self.description,
            'price': self.price,
            'receipt_text': self.receipt_text,
        }
        if inventory:
            ingredients = inventory['ingredients']
            exists = any(ingredient['id'] == self.id for ingredient in ingredients)
            data['missing'] = not exists
        return data

    def add_ean(self, ean_code):
        try:
            ean = EAN.query.filter_by(ean=ean_code).one()
            ean.ingredient = self
        except NoResultFound:
            ean = EAN()
            ean.ean = ean_code
            ean.ingredient = self
            db.session.add(ean)

    def from_product(self, product):
        # Image
        if 'image' in product and 'original' in product['image']:
            self.image = product['image']['original']
        # Receipt text
        if 'receipt_text' in product:
            self.receipt_text = product['receipt_text']
        # Description
        if 'description' in product and 'text' in product['description']:
            self.description = product['description']['text']
        # Regional information
        if 'regional_information' in product and 'national' in product['regional_information']:
            national = product['regional_information']['national']
            if 'price' in national and 'item' in national['price'] and 'price' in national['price']['item']:
                self.price = int(100 * float(national['price']['item']['price']))
        self.data = json.dumps(product)

    @staticmethod
    def get_by_id_or_ean(data):
        if 'id' in data:
            return Ingredient.query.filter_by(id=data['id']).first()
        elif 'ean' in data:
            ean = EAN.query.filter_by(ean=data['ean']).first()
            if ean:
                return ean.ingredient
        abort(404)

    @staticmethod
    def fetch(ean):
        url = 'http://api.autoidlabs.ch/products/%s?n=1' % ean
        r = requests.get(url)
        data = r.json()
        if not 'name' in data:
            abort(404)
        if 'name' in data:
            ingredient = Ingredient(data['name'], ean, data['image']['original'])
            db.session.add(ingredient)
        elif 'catPath' in data:
            ingredient = Ingredient(data['name'], ean, None)
            db.session.add(ingredient)
        else:
            ingredient = None
        if ingredient:
            ingredient.from_product(data)
        return ingredient


class Step(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500))
    description = db.Column(db.Text)
    image = db.Column(db.String(500))
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'))

    recipe = db.relationship(Recipe, backref=db.backref('steps', lazy='joined'), lazy='joined')

    def __init__(self, title=None, description=None, image=None, recipe=None):
        if not title:
            return
        self.title = title
        self.description = description
        self.image = image
        self.recipe = recipe

    def __str__(self):
        return "Step '%s'" % self.title

    def __repr__(self):
        return '<Step %r>' % self.id

    def to_json(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'image': self.image,
            'recipe': self.recipe_id,
        }


class ShoppingList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(500))
    recipe_id = db.Column(db.Integer, db.ForeignKey(Recipe.id))

    recipe = db.relationship(Recipe, backref=db.backref('shopping_lists', lazy='joined'), lazy='joined')
    ingredients = association_proxy('shopping_list_ingredients', 'ingredient')

    def __init__(self):
        pass

    def __str__(self):
        return "Sample Shopping List"

    def __repr__(self):
        return '<Shopping list %r>' % self.id

    def add_ingredient(self, ingredient, amount, unit):
        sli = ShoppingListIngredients(self, ingredient, amount, unit)
        db.session.add(sli)

    def to_json(self):
        return {
            'id': self.id,
            'user': self.user,
            'recipe': self.recipe.first().to_json(),
            'ingredients': list(map(to_json, self.ingredients.all())),
        }


class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(500))
    ingredients = association_proxy('inventory_ingredients', 'ingredient')

    def __init__(self, user=None):
        self.user = user

    def __repr__(self):
        return '<Inventory %r>' % self.id

    def __str__(self):
        return "Inventory of %s" % self.user

    def add_ingredient(self, ingredient, amount, unit):
        ri = InventoryIngredients(self, ingredient, amount, unit)
        db.session.add(ri)

    def to_json(self):
        return {
            'id': self.id,
            'user': self.user,
            'ingredients': list(map(to_json, self.ingredients)),
        }

    @staticmethod
    def get_current():
        return Inventory.query.first()


def to_json(obj):
    return obj.to_json()