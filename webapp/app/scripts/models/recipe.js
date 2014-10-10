/*global define*/

define([
    'underscore',
    'backbone'
], function (_, Backbone) {
    'use strict';

    var RecipeModel = Backbone.Model.extend({
        url: 'https://gist.githubusercontent.com/ynh/ce165d09e0c7f354a41a/raw/3b413a055aa9a7d9ccece841ed6b81d955d7f18c/gistfile1.txt',
 
    });

    return RecipeModel;
});
