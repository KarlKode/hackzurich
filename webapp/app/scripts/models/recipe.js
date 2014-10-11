/*global define*/

define([
    'underscore',
    'backbone'
], function (_, Backbone) {
    'use strict';

    var RecipeModel = Backbone.Model.extend({
        base_url: '/recipe/',
        url: function () { 
        	return window.base_url+this.base_url+this.id;
        },

	    parse: function(data) {
	    	if(data.recipe){
	        	return data.recipe;
	        }else{
	        	return data;
	        }
	    }
 
    });

    return RecipeModel;
});
