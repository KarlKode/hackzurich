/*global define*/

define([
    'underscore',
    'backbone'
], function (_, Backbone) {
    'use strict';

    var RecipeModel = Backbone.Model.extend({
        url: '',
 
    });

    return RecipeModel;
});
