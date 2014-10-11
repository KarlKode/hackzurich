/*global define*/

define([
    'jquery',
    'underscore',
    'backbone',
    'views/base',
    'templates'
], function ($, _, Backbone, BaseView, JST) {
    'use strict';

    var MenuView = BaseView.extend({
        template: JST['app/scripts/templates/menu.ejs'],

        className:'container',

        initialize: function () {
            Router.on('route', this.update_active, this);
        },

        after_render: function () {
            this.update_active();
        },

        update_active: function (argument) { 
            var item = null;
            var matchlength = -1;
            var active = window.location.hash + "";
            if (active === ""){
                active = "#";
            }
            var menu_items = this.$el.find('li'); 
            menu_items.each(function (){
                var url = $(this).find('a').data('match');
                if(url==undefined){
                    url = $(this).find('a').attr('href');
                }
                if (active.startsWith(url) && url.length > matchlength){
                    item = $(this);
                    matchlength = url.length;
                }
            });
            item && menu_items.removeClass('active'); 
            item && item.addClass('active');
        },

        dispose: function(){
          App.Router.off( null, null, this );
          BaseView.prototype.dispose.call(this);
        }
    });

    return MenuView;
});
