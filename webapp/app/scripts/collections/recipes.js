/*global define*/

define([
    'underscore',
    'backbone',
    'models/recipe'
], function (_, Backbone, RecipeModel) {
    'use strict';

    var RecipesCollection = Backbone.Collection.extend({
        model: RecipeModel,

        url: function (argument) {
            return         window.base_url+'/recipe';
        },

	    parse: function(data) {
	        return data.recipes;
	    }
    });

    return RecipesCollection;
});
