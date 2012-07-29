(function() {
  var root,
    __hasProp = Object.prototype.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; };

  root = typeof exports !== "undefined" && exports !== null ? exports : this;

  $(document).ready(function() {
    var SearchApplication;
    SearchApplication = (function(_super) {

      __extends(SearchApplication, _super);

      function SearchApplication() {
        SearchApplication.__super__.constructor.apply(this, arguments);
      }

      SearchApplication.prototype.jade = new root.Jade('/static/templates/search-application.jade');

      SearchApplication.prototype.paginatorJade = new root.Jade('/static/templates/paginator.jade');

      SearchApplication.prototype.limit = 10;

      SearchApplication.prototype.el = $('#page-content');

      SearchApplication.prototype.results = new Resources();

      SearchApplication.prototype.initialize = function(options) {
        this.render();
      };

      SearchApplication.prototype.render = function() {
        this.$el.append(this.jade.content({
          term: root.term
        }));
        return this;
      };

      SearchApplication.prototype.renderResults = function(results) {
        var result;
        $('#result-count').html("Your search returned " + results.total_rows + " results");
        root.app.results.reset((function() {
          var _i, _len, _ref, _results;
          _ref = results.results;
          _results = [];
          for (_i = 0, _len = _ref.length; _i < _len; _i++) {
            result = _ref[_i];
            _results.push(new Resource(result));
          }
          return _results;
        })());
        $('#results').empty();
        root.app.results.forEach(function(resource) {
          var resultView;
          resultView = new root.SearchResultView({
            model: resource
          });
          return $('#results').append(resultView.render().el);
        });
        return root.app.renderPaginator(results);
      };

      SearchApplication.prototype.renderPaginator = function(results) {
        var context, ele;
        if (results.total_rows < root.app.limit) return;
        context = {
          pageCount: Math.ceil(results.total_rows / root.app.limit),
          currentPage: (results.skip / root.app.limit) + 1
        };
        ele = $('#page-switcher');
        ele.empty();
        return ele.append(root.app.paginatorJade.content(context));
      };

      SearchApplication.prototype.events = {
        'click #search-button': 'searchButton',
        'keyup #search-terms': 'keycheck',
        'click .pager-item': 'pagination'
      };

      SearchApplication.prototype.doSearch = function(skip) {
        var options, postBody;
        if (skip == null) skip = 0;
        postBody = {
          searchTerms: escape($('#search-terms').val()),
          limit: root.app.limit,
          skip: skip
        };
        options = {
          type: 'POST',
          contentType: 'application/json',
          url: '/metadata/search/',
          data: JSON.stringify(postBody),
          processData: false,
          error: function(err) {
            return console.log(err);
          },
          success: root.app.renderResults
        };
        return $.ajax(options);
      };

      SearchApplication.prototype.searchButton = function(event) {
        return this.doSearch();
      };

      SearchApplication.prototype.keycheck = function(event) {
        if (event.keyCode === 13) return this.doSearch();
      };

      SearchApplication.prototype.pagination = function(event) {
        var buttonId, current, isNumber, skip;
        buttonId = event.target.id.split('-')[1];
        isNumber = function(n) {
          return !isNaN(parseFloat(n)) && isFinite(n);
        };
        if (isNumber(buttonId)) {
          skip = (parseInt(buttonId) - 1) * root.app.limit;
          return root.app.doSearch(skip);
        } else {
          current = $('.pager-current').attr('id').split('-')[1];
          switch (buttonId) {
            case 'first':
              return root.app.doSearch(0);
            case 'pre':
              skip = (current - 2) * root.app.limit;
              return root.app.doSearch(skip);
            case 'nxt':
              skip = current * root.app.limit;
              return root.app.doSearch(skip);
            case 'last':
              skip = (parseInt($('#pager-last').attr('last')) - 1) * root.app.limit;
              return root.app.doSearch(skip);
          }
        }
      };

      return SearchApplication;

    })(Backbone.View);
    root.app = new SearchApplication();
    if (root.term !== null && root.term !== '') return root.app.doSearch();
  });

}).call(this);
