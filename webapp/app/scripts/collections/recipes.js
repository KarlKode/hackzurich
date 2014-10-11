/*global define*/

define([
    'underscore',
    'backbone',
    'models/recipe'
], function (_, Backbone, RecipeModel) {
    'use strict';

    var RecipesCollection = Backbone.Collection.extend({
        model: RecipeModel,

        url: 'http://hackzurich.me/recipes',

	    parse: function(data) {
	        return data.recipes;
	    }
    });

    return RecipesCollection;
});
