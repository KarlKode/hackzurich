/*global define*/

define([
    'jquery',
    'underscore',
    'backbone',
    'views/base',
    'templates'
], function ($, _, Backbone, BaseView, JST) {
    'use strict';

    var DashboardView = BaseView.extend({
        template: JST['app/scripts/templates/main.ejs']
 
 
    });

    return DashboardView;
});
