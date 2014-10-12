/*global define*/

define([
    'jquery',
    'underscore',
    'backbone',
    'views/base',
    'templates',
    'views/menu'
], function ($, _, Backbone, BaseView, JST,MenuView) {
    'use strict';

    var FullscreenView = BaseView.extend({
        template: JST['app/scripts/templates/fullscreen.ejs'],
 

        initialize: function () { 
            $('body').addClass('fullscreen');
        },

        remove: function () { 
            $('body').removeClass('fullscreen'); 
        }
    });

    return FullscreenView;
});
