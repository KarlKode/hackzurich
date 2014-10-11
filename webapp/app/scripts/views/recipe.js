/*global define*/

define([
    'jquery',
    'underscore',
    'backbone',
    'views/base',
    'templates',
    'models/recipe',
    'bootstrap'
], function ($, _, Backbone, BaseView, JST, Recipe, bootstrap) {
    'use strict';

    var RecipeView = BaseView.extend({
        template: JST['app/scripts/templates/recipe.ejs'],
 
 
        initialize: function () {
            this.model = new Recipe();
            this.listenTo(this.model, 'change', this.render);
            BaseView.prototype.initialize.call(this);
            

        },

        events:{
            'click .cook_this': 'cook',
            'click .add_to_list': 'add_to_list',
            'click .done_shopping': 'done_shopping'
        },

        done_shopping: function(){
            this.model.fetch({reset:true});
        },

        add_to_list: function(e){
            e.preventDefault();
            var elements = _.map(this.$el.find('.ingredient:checked'), function(item){
                return {'ean':$(item).data('ean'),'amount':$(item).data('amount'),'unit':$(item).data('unit')};
            });
            $.ajax({
                contentType: 'application/json',
                data: JSON.stringify({ingredients:elements}),
                dataType: 'json',
                success: function(data){
                    $(".cook_recipe").modal('hide');
                    $(".done").modal();
                },
                error: function(){
                    alert("Device control failed");
                },
                processData: false,
                type: 'POST',
                url: window.base_url+'/shopping_list'
            }); 
        },

        cook: function(){
            $(".cook_recipe").modal();
        },

        after_render: function(){
 
        },

        set_attr:function (attrs) {
            this.model.id =attrs[0];
            this.model.fetch({reset:true});
        },
        get_data: function(){
            console.log(this.model.toJSON());
            return {recipe:this.model.toJSON()};
        }
    });

    return RecipeView;
});
