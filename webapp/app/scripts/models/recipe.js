/*global define*/

define([
    'underscore',
    'backbone'
], function (_, Backbone) {
    'use strict';

    var RecipeModel = Backbone.Model.extend({
        base_url: 'http://hackzurich.me/recipe/',
        url: function () {
        	return this.base_url+this.id;
        },

	    parse: function(data) {
	        return data.recipe;
	    }
 
    });

    return RecipeModel;
});
