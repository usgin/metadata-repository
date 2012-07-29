(function() {
  var root,
    __hasProp = Object.prototype.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; };

  root = typeof exports !== "undefined" && exports !== null ? exports : this;

  root.SearchResultView = (function(_super) {

    __extends(SearchResultView, _super);

    function SearchResultView() {
      SearchResultView.__super__.constructor.apply(this, arguments);
    }

    SearchResultView.prototype.jade = new root.Jade('/static/templates/search-result.jade');

    SearchResultView.prototype.tagName = 'dt';

    SearchResultView.prototype.render = function() {
      var context;
      context = {
        id: this.model.get('_id'),
        title: this.model.get('Title'),
        description: "" + (this.model.get('Description').substring(0, 225)) + " . . .",
        info: "" + (this.model.get('Authors')[0].Name) + " - Published on " + (this.model.get('PublicationDate')) + " - Modified on " + (this.model.get('ModifiedDate'))
      };
      this.$el.append(this.jade.content(context));
      return this;
    };

    return SearchResultView;

  })(Backbone.View);

}).call(this);
