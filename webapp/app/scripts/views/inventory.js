/*global define*/

define([
    'jquery',
    'underscore',
    'backbone',
    'views/base',
    'templates',
    'models/inventory',
    'selectize'
], function ($, _, Backbone, BaseView, JST, Inventory, selectize) {
    'use strict';

    var InventoryView = BaseView.extend({
        template: JST['app/scripts/templates/inventory.ejs'],
 
 
        initialize: function () {
            this.model = new Inventory();
            this.listenTo(this.model, 'change', this.render);
            BaseView.prototype.initialize.call(this);
            this.model.fetch({reset:true});

            var self=this;
            window.inventory=function(){self.model.fetch({reset:true})};
        },

        events: {
            'click .remove': 'removeItem',
            'click .add_to_inventory': 'add_to_inventory'
        },
        add_to_inventory: function(e){
            e.preventDefault();
            var selectize=this.$el.find('.add_item')[0].selectize;
            selectize.close(); 
            var items = _.map(selectize.getValue().split(','),function(x){
                return {id:x};
            });
            var self =this;
            $.ajax({
                contentType: 'application/json',
                data: JSON.stringify({inventory:items}),
                dataType: 'json',
                success: function(data){
                    self.model.fetch();
                },
                error: function(){
                    alert("Device control failed");
                },
                processData: false,
                type: 'POST',
                url: window.base_url+'/inventory'
            }); 
        },

        removeItem: function(e){
            e.preventDefault();
            var self = this;
            $.ajax({
                contentType: 'application/json',
                data: JSON.stringify({inventory:[{id:$(e.target).closest('a').data('id')}]}),
                dataType: 'json',
                success: function(data){
                    self.model.fetch();
                },
                error: function(){
                    alert("Device control failed");
                },
                processData: false,
                type: 'DELETE',
                url: window.base_url+'/inventory'
            }); 

        },

        after_render: function(){
            var REGEX_EMAIL = '[0-9]*';

this.$el.find('.add_item').selectize({
    persist: false,
    maxItems: null,
    valueField: 'id',
    labelField: 'title',
    searchField: ['title', 'id'], 
    render: {
        item: function(item, escape) {
            return '<div>' + 
                (item.title ? '<span class="name">' + escape(item.title) + '</span>' : '') +
              
            '</div>';
        },
        option: function(item, escape) {
            var label = item.title || item.id;
            var caption = item.id ? item.title : null;
            return '<div>' +
                '<b >' + escape(label) + '</b> ' + 
            '</div>';
        }
    },
    createFilter: function(input) {
        var match, regex;

        // email@address.com
        regex = new RegExp('^' + REGEX_EMAIL + '$', 'i');
        match = input.match(regex);
        if (match) return !this.options.hasOwnProperty(match[0]);

        // name <email@address.com>
        regex = new RegExp('^([^<]*)\<' + REGEX_EMAIL + '\>$', 'i');
        match = input.match(regex);
        if (match) return !this.options.hasOwnProperty(match[2]);

        return false;
    },
      load: function(query, callback) {
        if (!query.length){
            return callback([]);

        }
        $.ajax({
            url: window.base_url+'/ingredient',
            type: 'GET',
            dataType: 'json', 
            data: {
                q: query
            },
            error: function() {
                callback();
            },
            success: function(res) { 
                callback(res.ingredients);
            }
        });
    },
    create: function(input) {
        if ((new RegExp('^' + REGEX_EMAIL + '$', 'i')).test(input)) {
            return {ean: input};
        } 
        alert('Invalid ean address.');
        return false;
    }
});
        },
        get_data: function(){
            return {ingredients:this.model.toJSON().ingredients};
        },
        remove:function(){

            window.inventory=function(){};
        }
    });

    return InventoryView;
});
