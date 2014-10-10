/*global define*/

define([
    'jquery',
    'underscore',
    'backbone',
    'views/base',
    'templates'
], function ($, _, Backbone, BaseView, JST) {
    'use strict';

    var LayoutView = BaseView.extend({
        template: JST['app/scripts/templates/layout.ejs'],
 

        initialize: function () {
         //   this.subviews = {'#menu':new MenuView()}
        }
    });

    return LayoutView;
});
