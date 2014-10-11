from flask import abort
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.ext.associationproxy import association_proxy

db = SQLAlchemy()


class RecipeIngredients(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'))
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredient.id'))
    amount = db.Column(db.String(100))
    unit = db.Column(db.String(100))

    recipe = db.relationship('Recipe', backref='recipe_ingredients')
    ingredient = db.relationship('Ingredient', backref='recipe_ingredients')

    def __init__(self, recipe, ingredient, amount, unit):
        self.recipe = recipe
        self.ingredient = ingredient
        self.amount = amount
        self.unit = unit


class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    images = db.Column(db.Text)
    difficulty = db.Column(db.Integer)
    duration = db.Column(db.Integer)

    ingredients = association_proxy('recipe_ingredients', 'ingredient')

    def __init__(self, title, difficulty, duration, images=None):
        self.title = title
        self.difficulty = difficulty
        self.duration = duration
        self.images = images

    def __repr__(self):
        return '<Recipe %r>' % self.id

    def add_ingredient(self, ingredient):
        ri = RecipeIngredients(self, ingredient, None, None)
        db.session.add(ri)

    def to_json(self, inventory=None):
        ingredients = list(map(lambda i: i.to_json(inventory), self.ingredients))
        return {
            'id': self.id,
            'title': self.title,
            'images': self.images,
            'difficulty': self.difficulty,
            'duration': self.duration,
            'ingredients': ingredients,
            'missing': sum(1 for i in ingredients if i['missing']),
            'steps': list(map(lambda s: s.to_json(), self.steps))
        }


class ShoppingListIngredients(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    shopping_list_id = db.Column(db.Integer, db.ForeignKey('shopping_list.id'))
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredient.id'))
    amount = db.Column(db.String(100))
    unit = db.Column(db.String(100))

    shopping_list = db.relationship('ShoppingList', backref='shopping_list_ingredients')
    ingredient = db.relationship('Ingredient', backref='shopping_list_ingredients')

    def __init__(self, shopping_list, ingredient, amount, unit):
        self.shopping_list = shopping_list
        self.ingredient = ingredient
        self.amount = amount
        self.unit = unit


class InventoryIngredients(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventory.id'))
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredient.id'))
    amount = db.Column(db.String(100))
    unit = db.Column(db.String(100))

    inventory = db.relationship('Inventory', backref='inventory_ingredients')
    ingredient = db.relationship('Ingredient', backref='inventory_ingredients')

    def __init__(self, inventory, ingredient, amount, unit):
        self.inventory = inventory
        self.ingredient = ingredient
        self.amount = amount
        self.unit = unit


class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    ean = db.Column(db.Integer)
    image = db.Column(db.String(200))

    shopping_lists = association_proxy('shopping_list_ingredients', 'shopping_list')
    inventories = association_proxy('inventory_ingredients', 'inventory')

    def __init__(self, title, ean, image=None):
        self.title = title
        self.ean = ean
        self.image = image

    def __repr__(self):
        return '<Ingredient %r>' % self.id

    def to_json(self, inventory=None):
        data = {
            'id': self.id,
            'title': self.title,
            'ean': self.ean,
            'image': self.image,
        }
        if inventory:
            print(inventory)
            ingredients = inventory['ingredients']
            exists = any(ingredient['id']==self.id for ingredient in ingredients)
            data['missing'] = not exists
        return data

    @staticmethod
    def get_by_id_or_ean(data):
        if 'id' in data:
            return Ingredient.query.get(id=data['id'])
        elif 'ean' in data:
            return Ingredient.query.get(ean=data['ean'])
        abort(404)


class Step(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    image = db.Column(db.String(200))
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'))

    recipe = db.relationship(Recipe, backref='steps')

    def __init__(self):
        pass

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
    user = db.Column(db.String(100))
    recipe_id = db.Column(db.Integer, db.ForeignKey(Recipe.id))

    recipe = db.relationship(Recipe, backref='shopping_lists')
    ingredients = association_proxy('shopping_list_ingredients', 'ingredient')

    def __init__(self):
        self.recipe = None

    def __repr__(self):
        return '<Recipe %r>' % self.id

    def add_ingredient(self, ingredient):
        sli = ShoppingListIngredients(self, ingredient, None, None)
        db.session.add(sli)

    def to_json(self):
        return {
            'id': self.id,
            'user': self.user,
            'recipe': self.recipe.first().to_json(),
            'ingredients': map(lambda i: i.to_json(), self.ingredients.all()),
        }


class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(100))
    ingredients = association_proxy('inventory_ingredients', 'ingredient')

    def __init__(self):
        pass

    def __repr__(self):
        return '<Inventory %r>' % self.id

    def add_ingredient(self, ingredient):
        ri = InventoryIngredients(self, ingredient, None, None)
        db.session.add(ri)

    def to_json(self):
        return {
            'id': self.id,
            'user': self.user,
            'ingredients': list(map(lambda i: i.to_json(), self.ingredients)),
        }
