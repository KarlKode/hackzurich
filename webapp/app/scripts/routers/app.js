/*global define*/

define([
    'jquery',
    'backbone',
    'views/layout',
    'views/main'
], function ($, Backbone, LayoutView, MainView) {
    'use strict';

    var AppRouter = Backbone.Router.extend({
        routes: {
            '': 'index'
        },

        views: {
            'MainView': MainView
        },

        current_layout: null,

        last_hash:null,

        modal:null,

        current_view: null,

        layouts: {
            'main': function(){
                return new LayoutView();
            }
        },
 
        index: function (argument) {
            this.loadView('main', 'MainView', arguments);
        },  

        loadView : function(layout, view, attr) {
            if (this.modal !== null){
                this.modal.$el.modal('hide');
                this.modal.dispose();
                this.modal = null;
            }
            if(this.last_hash==window.location.hash){
                return;
            }
            this.last_hash=window.location.hash;
            if (this.current_view == view){
                this.view.set_attr(attr);
                return;
            }
            this.view && this.view.dispose();
            if (this.current_layout !== layout){
                this.current_layout = layout;
                this.layout && this.layout.dispose();
                this.layout = this.layouts[layout]();
                $("#app").html(this.layout.$el);
                this.layout.render();
            }
            this.view = new this.views[view]();
            this.view.set_attr(attr);
            this.current_view = view;
            this.layout.$el.find("#content").html(this.view.$el);
            this.view.render();
        }

    });

    return AppRouter;
});