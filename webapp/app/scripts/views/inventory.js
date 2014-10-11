/*global define*/

define([
    'jquery',
    'underscore',
    'backbone',
    'views/base',
    'templates',
    'models/inventory',
], function ($, _, Backbone, BaseView, JST, Inventory) {
    'use strict';

    var InventoryView = BaseView.extend({
        template: JST['app/scripts/templates/inventory.ejs'],
 
 
        initialize: function () {
            this.model = new Inventory();
            this.listenTo(this.model, 'change', this.render);
            BaseView.prototype.initialize.call(this);
            this.model.fetch({reset:true});

        },

        get_data: function(){
            return {ingredients:this.model.toJSON().ingredients};
        }
    });

    return InventoryView;
});
