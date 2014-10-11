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
                return {ean:x};
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
                data: JSON.stringify({inventory:[{ean:$(e.target).closest('a').data('ean')}]}),
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
    valueField: 'ean',
    labelField: 'title',
    searchField: ['title', 'ean'], 
    render: {
        item: function(item, escape) {
            return '<div>' +
              (item.ean ? '<span class="email">' + escape(item.ean) + '</span> ' : '') +
                (item.title ? '<span class="name">' + escape(item.title) + '</span>' : '') +
              
            '</div>';
        },
        option: function(item, escape) {
            var label = item.ean || item.title;
            var caption = item.ean ? item.title : null;
            return '<div>' +
                '<b>' + escape(label) + '</b> ' +
                (caption ? '<span class="caption">' + escape(caption) + '</span>' : '') +
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
        if (!query.length) return callback();
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
        }
    });

    return InventoryView;
});
