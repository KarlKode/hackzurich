/*global define*/

define([
    'jquery',
    'underscore',
    'backbone',
    'views/base',
    'templates',
    'collections/ingredients',
], function ($, _, Backbone, BaseView, JST, IngredientsCollection) {
    'use strict';

    var IngredientsView = BaseView.extend({
        template: JST['app/scripts/templates/ingredients.ejs'],
 
 
        initialize: function () {
            this.collection = new IngredientsCollection();
            this.listenTo(this.collection, 'reset', this.render);
            BaseView.prototype.initialize.call(this);
            this.collection.fetch({reset:true});

        },

        get_data: function(){
            return {ingredients:this.collection.toJSON()};
        }
    });

    return IngredientsView;
});
