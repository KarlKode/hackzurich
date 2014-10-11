/*global define*/

define([
    'jquery',
    'backbone',
    'views/layout',
    'views/fullscreen',
    'views/main',
    'views/recipes',
    'views/recipe',
    'views/inventory',
    'views/ingredients',
    'views/shopping_list',
    'views/presenter'
], function ($, Backbone, LayoutView, FullscreenView, MainView, RecipesView, RecipeView, InventoryView, IngredientsView, ShoppingListView, PresenterView) {
    'use strict';

    var AppRouter = Backbone.Router.extend({
        routes: {
            '': 'index',
            'recipes': 'recipes',
            'inventory': 'inventory',
            'recipes/:id': 'recipe',
            'ingredients': 'ingredients',
            'shopping_list': 'shopping_list',
            'presenter/:id': 'presenter'
        },

        views: {
            'MainView': MainView,

            'RecipesView': RecipesView,

            'RecipeView': RecipeView,
            'InventoryView':InventoryView,
            'IngredientsView':IngredientsView,
            'ShoppingListView':ShoppingListView,
            'PresenterView':PresenterView
        },

        current_layout: null,

        last_hash:null,

        modal:null,

        current_view: null,

        layouts: {
            'main': function(){
                return new LayoutView();
            },
            'fullscreen': function(){
                return new FullscreenView();
            }
        },
 
        index: function (argument) {
            this.loadView('main', 'MainView', arguments);
        }, 
 
        presenter: function (argument) {
            this.loadView('fullscreen', 'PresenterView', arguments);
        },  

        recipes: function (argument) {
            this.loadView('main', 'RecipesView', arguments);
        },

        ingredients: function (argument) {
            this.loadView('main', 'IngredientsView', arguments);
        },

        shopping_list: function (argument) {
            this.loadView('main', 'ShoppingListView', arguments);
        },

        inventory: function (argument) {
            this.loadView('main', 'InventoryView', arguments);
        },  

        recipe: function (argument) {
            this.loadView('main', 'RecipeView', arguments);
        },  

        loadView : function(layout, view, attr) {
            if (this.modal !== null){
                this.modal.$el.modal('hide');
                this.modal.dispose();
                this.modal = null;
            }
            if(this.last_hash==window.location.hash){
                return;
            }
            this.last_hash=window.location.hash;
            if (this.current_view == view){
                this.view.set_attr(attr);
                return;
            }
            this.view && this.view.dispose();
            if (this.current_layout !== layout){
                this.current_layout = layout;
                this.layout && this.layout.dispose();
                this.layout = this.layouts[layout]();
                $("#app").html(this.layout.$el);
                this.layout.render();
            }
            this.view = new this.views[view]();
            this.view.set_attr(attr);
            this.current_view = view;
            this.layout.$el.find("#content").html(this.view.$el);
            this.view.render();
        }

    });

    return AppRouter;
});
