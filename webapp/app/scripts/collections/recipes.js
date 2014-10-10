/*global define*/

define([
    'underscore',
    'backbone',
    'models/recipe'
], function (_, Backbone, RecipeModel) {
    'use strict';

    var RecipesCollection = Backbone.Collection.extend({
        model: RecipeModel,

        url: 'https://gist.githubusercontent.com/ynh/53c50bae7c68ed4a655a/raw/6fa0af421bff3710b0d8ec8dfcefff1582541479/gistfile1.txt',

	    parse: function(data) {
	        return data.recipes;
	    }
    });

    return RecipesCollection;
});
