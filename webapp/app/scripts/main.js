/*global require*/
'use strict';

require.config({
    shim: {
        bootstrap: {
            deps: ['jquery','arrive','material'],
            exports: 'jquery'
        }
    },
    paths: {
        jquery: '../bower_components/jquery/dist/jquery',
        backbone: '../bower_components/backbone/backbone',
        selectize: '../bower_components/selectize/dist/js/selectize.min',
        sifter: '../bower_components/sifter/sifter',
        microplugin:'../bower_components/microplugin/src/microplugin',
        'arrive': '../vendors/arrive-2.0.0.min',
        'material': '../bower_components/bootstrap-material-design/scripts/material',
        underscore: '../bower_components/underscore/underscore',
        bootstrap: '../bower_components/sass-bootstrap/dist/js/bootstrap'
    }
});
if (typeof String.prototype.startsWith != 'function') {
  // see below for better implementation!
  String.prototype.startsWith = function (str){
    return this.indexOf(str) == 0;
  };
}
window.base_url = "http://hackzurich.me";
//window.base_url = "http://127.0.0.1:5000";
require([
    'backbone', 'routers/app'
], function (Backbone, App) {
    window.Router = new App();
    Backbone.history.start();
});
