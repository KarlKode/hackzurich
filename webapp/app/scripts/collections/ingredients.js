/*global define*/

define([
    'underscore',
    'backbone',
    'models/recipe'
], function (_, Backbone, RecipeModel) {
    'use strict';

    var IngredientsCollection = Backbone.Collection.extend({
        model: RecipeModel,

        url: function (argument) {
            return         window.base_url+'/ingredient';
        },

	    parse: function(data) {
	        return data.ingredients;
	    }
    });

    return IngredientsCollection;
});
