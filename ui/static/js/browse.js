(function() {
  var root,
    __hasProp = Object.prototype.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; };

  root = typeof exports !== "undefined" && exports !== null ? exports : this;

  $(document).ready(function() {
    var CollectionBrowser;
    CollectionBrowser = (function(_super) {

      __extends(CollectionBrowser, _super);

      function CollectionBrowser() {
        CollectionBrowser.__super__.constructor.apply(this, arguments);
      }

      CollectionBrowser.prototype.topCollections = new root.ResourceCollections();

      CollectionBrowser.prototype.el = $('#collection-list');

      CollectionBrowser.prototype.initialize = function() {
        var col, _i, _len, _ref;
        _ref = root.collections;
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          col = _ref[_i];
          this.topCollections.add(new root.ResourceCollection(col));
        }
        this.renderCollections();
      };

      CollectionBrowser.prototype.render = function() {
        return this;
      };

      CollectionBrowser.prototype.renderCollections = function() {
        var that;
        that = this;
        this.topCollections.forEach(function(collection) {
          var topView;
          topView = new root.TopCollectionView({
            model: collection
          });
          that.$el.append(topView.render().el);
        });
      };

      return CollectionBrowser;

    })(Backbone.View);
    root.application = new CollectionBrowser();
  });

}).call(this);
