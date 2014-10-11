/*global define*/

define([
    'underscore',
    'backbone'
], function (_, Backbone) {
    'use strict';

    var InventoryModel = Backbone.Model.extend({
        url: function () { 
        	return window.base_url+'/shopping_list';
        },

	    parse: function(data) { 
	        	return data; 
	    }
 
    });

    return InventoryModel;
});
