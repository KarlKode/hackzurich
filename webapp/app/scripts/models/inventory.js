/*global define*/

define([
    'underscore',
    'backbone'
], function (_, Backbone) {
    'use strict';

    var InventoryModel = Backbone.Model.extend({
        url: function () { 
        	return window.base_url+'/inventory';
        },

	    parse: function(data) { 
	        	return data.inventory; 
	    }
 
    });

    return InventoryModel;
});
