/*global define*/

define([
    'jquery',
    'underscore',
    'backbone',
    'views/base',
    'templates',
    'collections/recipes',
], function ($, _, Backbone, BaseView, JST, RecipesCollection) {
    'use strict';

    var InventoryView = BaseView.extend({
        template: JST['app/scripts/templates/inventory.ejs'],
 
 
        initialize: function () {
            this.collection = new RecipesCollection();
            this.listenTo(this.collection, 'reset', this.render);
            BaseView.prototype.initialize.call(this);
            this.collection.fetch({reset:true});

        },

        get_data: function(){
            return {recipes:this.collection.toJSON()};
        }
    });

    return InventoryView;
});
