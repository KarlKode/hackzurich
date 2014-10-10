/*global define*/

define([
    'jquery',
    'underscore',
    'backbone',
    'views/base',
    'templates',
    'models/recipe',
], function ($, _, Backbone, BaseView, JST, Recipe) {
    'use strict';

    var RecipeView = BaseView.extend({
        template: JST['app/scripts/templates/recipe.ejs'],
 
 
        initialize: function () {
            this.model = new Recipe();
            this.listenTo(this.model, 'change', this.render);
            BaseView.prototype.initialize.call(this);
            this.model.fetch({reset:true});

        },

        get_data: function(){
            console.log(this.model.toJSON());
            return {recipe:this.model.toJSON()};
        }
    });

    return RecipeView;
});
