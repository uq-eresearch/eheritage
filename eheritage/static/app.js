
App = Ember.Application.create();

App.Router.map(function() {
    this.resource('search');
});

App.SearchRoute = Ember.Route.extend({
    model: function(params) {
        return $.getJSON('/search/', params).then(function(data) {
            return data;
            // // Translate data to a better format
            // return data.posts.map(function(post) {
            //     post.body = post.content;
            //     return post;
            // });
        });
    },
    actions: {
        queryParamsDidChange: function() {
          // This is how we opt-in to
          // a full-on transition that'll
          // refire the `model` hook and 
          // give us a chance to reload data
          // from the server.
          this.refresh();
        },
    }
});
// Helper computed property used by nextPage
// and previousPage.
var incrementPage = function(amt) {
  return Ember.computed('page', 'numPages', function() {
    var newPage = this.get('page') + amt;
    if (newPage <= this.get('numPages') &&
        newPage >= 1) {
      return newPage;
    }
  });
};
App.SearchController = Ember.ObjectController.extend({
    queryParams: ['keyword', 'page'],
    keyword: null,
    page: 1,
    pageSize: 10,

    keywordField: Ember.computed.oneWay('keyword'),


    pages: function() {
        var pageSize = this.get('pageSize'),
            l = this.get('model.count'),
            pages = Math.ceil(l / pageSize),
            pagesArray = [];

        for(var i = 0; i < pages; i ++) {
            pagesArray.push(i + 1);
        }

        return pagesArray;
    }.property('pageSize', 'model.count'),

    numPages: function() {
        var pageSize = this.get('pageSize'),
            l = this.get('model.count');
        return Math.ceil(l / pageSize);
    }.property('pageSize'),

    previousPage: incrementPage(-1),
    nextPage:     incrementPage(1),

    actions: {
        search: function() {
            // search logic
            this.set('keyword', this.get('keywordField'))
        }
    }
});




// App.ResultsRoute = Ember.Route.extend({
//     model: function() {
//         return $.getJSON().then(function(data) {
//             // Translate data to a better format
//             return data.posts.map(function(post) {
//                 post.body = post.content;
//                 return post;
//             });
//         });
//     }
// });