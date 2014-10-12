/*global define*/

define([
    'jquery',
    'underscore',
    'backbone',
    'views/base',
    'templates',
    'models/recipe'
], function ($, _, Backbone, BaseView, JST, Recipe) {
    'use strict';

    var RecipesView = BaseView.extend({
        template: JST['app/scripts/templates/presenter.ejs'],
 
 
        initialize: function () {
            this.model = new Recipe();
            this.listenTo(this.model, 'change', this.render);
            BaseView.prototype.initialize.call(this);
        },

        // get_data: function(){
        //     return {recipes:this.collection.toJSON()};
        // }
        after_render: function(){
            this.$el.find('.carousel').carousel({
  interval: 200000
});
            this.$el.find('.item').height(window.innerHeight);
            if(this.recognition!=null){
                this.recognition.stop();
            }
            this.recognition = new webkitSpeechRecognition();
             this.recognition.continuous = true;
              this.recognition.interimResults = true;
             

              this.recognition.onresult = function(event) {
                var final_transcript= '';
                for (var i = event.resultIndex; i < event.results.length; ++i) {
                  if (event.results[i].isFinal) {
                    final_transcript += event.results[i][0].transcript;
                  } else {
                    interim_transcript += event.results[i][0].transcript;
                  }
                }
                alert(final_transcript);
              };
            this.recognition.start();
        },
        set_attr:function (attrs) {
            this.model.id =attrs[0];
            this.model.fetch({reset:true});
        },
        get_data: function(){
            console.log(this.model.toJSON());
            return {recipe:this.model.toJSON()};
        },
        remove:function(){
            if(this.recognition!=null){
                this.recognition.stop();
            }
        }
    });

    return RecipesView;
});
