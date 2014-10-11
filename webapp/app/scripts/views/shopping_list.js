/*global define*/

define([
    'jquery',
    'underscore',
    'backbone',
    'views/base',
    'templates',
    'models/shopping_list',
], function ($, _, Backbone, BaseView, JST, ShoppingList) {
    'use strict';

    var ShoppingListView = BaseView.extend({
        template: JST['app/scripts/templates/shopping_list.ejs'],
 
 
        initialize: function () {
            this.model = new ShoppingList();
            this.listenTo(this.model, 'change', this.render);
            BaseView.prototype.initialize.call(this);
            this.model.fetch({reset:true});

        },

        events: {
            'click .remove': 'removeItem'
        },

        removeItem: function(e){
            e.preventDefault();
            var self = this;
            $.ajax({
                contentType: 'application/json',
                data: JSON.stringify({ingredients:[{ean:$(e.target).closest('a').data('ean')}]}),
                dataType: 'json',
                success: function(data){
                    self.model.fetch();
                },
                error: function(){
                    alert("Device control failed");
                },
                processData: false,
                type: 'DELETE',
                url: window.base_url+'/shopping_list'
            }); 

        },

        get_data: function(){
            return {ingredients:this.model.toJSON().ingredients};
        }
    });

    return ShoppingListView;
});
