(function() {
  var addNewCollection, root,
    __hasProp = Object.prototype.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; };

  root = typeof exports !== "undefined" && exports !== null ? exports : this;

  addNewCollection = function(view, collectionId) {
    $('#page-content').append(view.newCollectionJade.content({
      parentCollection: view.model.get('title')
    }));
    return $('#new-collection-dialog').dialog({
      resizable: false,
      width: 500,
      modal: true,
      buttons: {
        "Create New Collection": function() {
          var desc, opts, title;
          title = $('#new-collection-title').val();
          desc = $('#new-collection-description').val();
          opts = {
            type: 'POST',
            url: '/metadata/collection/',
            contentType: 'application/json',
            processData: false,
            data: JSON.stringify({
              Title: title,
              Description: desc,
              ParentCollections: [collectionId]
            }),
            error: function(err) {
              return console.log(err);
            },
            success: function(data, status, xhr) {
              var id, loc;
              loc = xhr.getResponseHeader('Location');
              id = loc.match(/collection\/(.*)\/$/)[1];
              view.model.collections.add(new root.ResourceCollection({
                id: id,
                title: title,
                description: desc,
                can_edit: true
              }));
              view.render();
              if (view.$el.find('.collection-content > .record-list').first().hasClass('hidden')) {
                view.expand();
              }
              $('#new-collection-dialog').dialog('close');
              return $('#new-collection-dialog').remove();
            }
          };
          return $.ajax(opts);
        },
        Cancel: function() {
          $(this).dialog('close');
          return $(this).remove();
        }
      }
    });
  };

  root.TopCollectionView = (function(_super) {

    __extends(TopCollectionView, _super);

    function TopCollectionView() {
      TopCollectionView.__super__.constructor.apply(this, arguments);
    }

    TopCollectionView.prototype.jade = new root.Jade('/static/templates/top-collection.jade');

    TopCollectionView.prototype.newCollectionJade = new root.Jade('/static/templates/add-new-collection.jade');

    TopCollectionView.prototype.tagName = 'div';

    TopCollectionView.prototype.className = 'collection-container';

    TopCollectionView.prototype.initialize = function(options) {
      this.collectionId = options.model.id;
    };

    TopCollectionView.prototype.render = function() {
      var thisView, ul;
      this.$el.empty();
      this.$el.append(this.jade.content(this.model.toJSON()));
      ul = this.$el.find('.collection-content > .record-list').first();
      thisView = this;
      this.model.collections.forEach(function(collection) {
        var childView;
        childView = new root.ChildCollectionView({
          model: collection,
          parent: thisView
        });
        return ul.append(childView.render().el);
      });
      this.model.resources.forEach(function(resource) {
        var resourceView;
        resourceView = new root.ChildResourceView({
          model: resource,
          parent: thisView
        });
        return ul.append(resourceView.render().el);
      });
      return this;
    };

    TopCollectionView.prototype.events = {
      'click .expand:first': 'expand',
      'click .addCollection:first': 'addCollection',
      'click .addRecord:first': 'addRecord'
    };

    TopCollectionView.prototype.expand = function() {
      var tri, ul;
      ul = this.$el.find('.collection-content > .record-list').first();
      tri = this.$el.find('.collection-list-expand').first();
      if (ul.hasClass('hidden')) {
        ul.removeClass('hidden');
        tri.removeClass('ui-icon-triangle-1-e');
        return tri.addClass('ui-icon-triangle-1-s');
      } else {
        ul.addClass('hidden');
        tri.removeClass('ui-icon-triangle-1-s');
        return tri.addClass('ui-icon-triangle-1-e');
      }
    };

    TopCollectionView.prototype.addCollection = function(event) {
      return addNewCollection(this, this.collectionId);
    };

    TopCollectionView.prototype.addRecord = function(event) {
      return window.location.href = "/repository/collection/" + this.collectionId + "/resource/new";
    };

    return TopCollectionView;

  })(Backbone.View);

  root.ChildCollectionView = (function(_super) {

    __extends(ChildCollectionView, _super);

    function ChildCollectionView() {
      ChildCollectionView.__super__.constructor.apply(this, arguments);
    }

    ChildCollectionView.prototype.jade = new root.Jade('/static/templates/child-collection.jade');

    ChildCollectionView.prototype.newCollectionJade = new root.Jade('/static/templates/add-new-collection.jade');

    ChildCollectionView.prototype.confirmationJade = new root.Jade('/static/templates/confirmation-dialog.jade');

    ChildCollectionView.prototype.tagName = 'li';

    ChildCollectionView.prototype.className = 'record-container collection-item collection-container';

    ChildCollectionView.prototype.initialize = function(options) {
      if (options.parent != null) this.parentView = options.parent;
      this.collectionId = options.model.id;
    };

    ChildCollectionView.prototype.render = function() {
      var thisView, ul;
      this.$el.empty();
      this.$el.append(this.jade.content(this.model.toJSON()));
      ul = this.$el.find('ul.record-list').first();
      thisView = this;
      this.model.collections.forEach(function(collection) {
        var childView;
        childView = new root.ChildCollectionView({
          model: collection,
          parent: thisView
        });
        return ul.append(childView.render().el);
      });
      this.model.resources.forEach(function(resource) {
        var resourceView;
        resourceView = new root.ChildResourceView({
          model: resource,
          parent: thisView
        });
        return ul.append(resourceView.render().el);
      });
      return this;
    };

    ChildCollectionView.prototype.events = {
      'click .expand:first': 'expand',
      'click .addCollection:first': 'addCollection',
      'click .addRecord:first': 'addRecord',
      'click .deleteCollection:first': 'deleteCollection'
    };

    ChildCollectionView.prototype.expand = function() {
      var tri, ul;
      ul = this.$el.find('ul.record-list').first();
      tri = this.$el.find('.collection-list-expand').first();
      if (ul.hasClass('hidden')) {
        ul.removeClass('hidden');
        tri.removeClass('ui-icon-triangle-1-e');
        return tri.addClass('ui-icon-triangle-1-s');
      } else {
        ul.addClass('hidden');
        tri.removeClass('ui-icon-triangle-1-s');
        return tri.addClass('ui-icon-triangle-1-e');
      }
    };

    ChildCollectionView.prototype.addCollection = function(event) {
      return addNewCollection(this, this.collectionId);
    };

    ChildCollectionView.prototype.addRecord = function(event) {
      return window.location.href = "/repository/collection/" + this.collectionId + "/resource/new";
    };

    ChildCollectionView.prototype.deleteCollection = function(event) {
      var view;
      console.log("remove the collection " + this.collectionId + " from " + this.parentView.collectionId);
      view = this;
      $('#page-content').append(view.confirmationJade.content({
        title: 'Remove Child Collection?',
        message: 'Are you sure you want to remove this collection from its parent?'
      }));
      return $('#dialog-confirm').dialog({
        resizable: false,
        width: 400,
        modal: true,
        buttons: {
          "Remove": function() {
            var getOpts;
            getOpts = {
              type: 'GET',
              url: "/metadata/collection/" + view.collectionId + "/",
              error: function(err) {
                return console.log(err);
              },
              success: function(data, status, xhr) {
                var col, putOpts;
                data.ParentCollections = (function() {
                  var _i, _len, _ref, _results;
                  _ref = data.ParentCollections;
                  _results = [];
                  for (_i = 0, _len = _ref.length; _i < _len; _i++) {
                    col = _ref[_i];
                    if (col !== view.parentView.collectionId) _results.push(col);
                  }
                  return _results;
                })();
                putOpts = {
                  type: 'PUT',
                  url: "/metadata/collection/" + view.collectionId + "/",
                  contentType: 'application/json',
                  processData: false,
                  data: JSON.stringify(data),
                  error: function(err) {
                    return console.log(err);
                  },
                  success: function(data, status, xhr) {
                    return console.log(status);
                  }
                };
                return $.ajax(putOpts);
              }
            };
            $.ajax(getOpts);
            view.parentView.model.collections.remove(view.model);
            view.parentView.render();
            view.parentView.expand();
            $(this).dialog('close');
            return $(this).remove();
          },
          Cancel: function() {
            $(this).dialog('close');
            return $(this).remove();
          }
        }
      });
    };

    return ChildCollectionView;

  })(Backbone.View);

  root.ChildResourceView = (function(_super) {

    __extends(ChildResourceView, _super);

    function ChildResourceView() {
      ChildResourceView.__super__.constructor.apply(this, arguments);
    }

    ChildResourceView.prototype.jade = new root.Jade('/static/templates/child-resource.jade');

    ChildResourceView.prototype.confirmationJade = new root.Jade('/static/templates/confirmation-dialog.jade');

    ChildResourceView.prototype.tagName = 'li';

    ChildResourceView.prototype.className = 'record-container';

    ChildResourceView.prototype.initialize = function(options) {
      if (options.parent != null) this.parentView = options.parent;
      this.resourceId = options.model.id;
    };

    ChildResourceView.prototype.render = function() {
      this.$el.append(this.jade.content(this.model.toJSON()));
      return this;
    };

    ChildResourceView.prototype.events = {
      'click .deleteRecord:first': 'deleteRecord'
    };

    ChildResourceView.prototype.deleteRecord = function() {
      var view;
      console.log("Remove record " + this.resourceId + " from " + this.parentView.collectionId);
      view = this;
      $('#page-content').append(view.confirmationJade.content({
        title: 'Remove Child Resource?',
        message: 'Are you sure you want to remove this resource from its collection?'
      }));
      return $('#dialog-confirm').dialog({
        resizable: false,
        width: 400,
        modal: true,
        buttons: {
          "Remove": function() {
            var getOpts;
            getOpts = {
              type: 'GET',
              url: "/metadata/record/" + view.resourceId + "/",
              error: function(err) {
                return console.log(err);
              },
              success: function(data, status, xhr) {
                var col, putOpts;
                data.Collections = (function() {
                  var _i, _len, _ref, _results;
                  _ref = data.Collections;
                  _results = [];
                  for (_i = 0, _len = _ref.length; _i < _len; _i++) {
                    col = _ref[_i];
                    if (col !== view.parentView.collectionId) _results.push(col);
                  }
                  return _results;
                })();
                putOpts = {
                  type: 'PUT',
                  url: "/metadata/record/" + view.resourceId + "/",
                  contentType: 'application/json',
                  processData: false,
                  data: JSON.stringify(data),
                  error: function(err) {
                    return console.log(err);
                  },
                  success: function(data, status, xhr) {
                    return console.log(status);
                  }
                };
                return $.ajax(putOpts);
              }
            };
            $.ajax(getOpts);
            view.parentView.model.resources.remove(view.model);
            view.parentView.render();
            view.parentView.expand();
            $(this).dialog('close');
            return $(this).remove();
          },
          Cancel: function() {
            $(this).dialog('close');
            return $(this).remove();
          }
        }
      });
    };

    return ChildResourceView;

  })(Backbone.View);

}).call(this);
