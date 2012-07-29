(function() {
  var root,
    __hasProp = Object.prototype.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; };

  root = typeof exports !== "undefined" && exports !== null ? exports : this;

  $(document).ready(function() {
    var App;
    App = (function(_super) {

      __extends(App, _super);

      function App() {
        App.__super__.constructor.apply(this, arguments);
      }

      App.prototype.record = new Resource(root.inputRecord || {});

      App.prototype.collections = new ResourceCollections();

      App.prototype.schemas = {};

      App.prototype.contactJade = new root.Jade('/static/templates/select-contact-dialog.jade');

      App.prototype.confirmationJade = new root.Jade('/static/templates/confirmation-dialog.jade');

      App.prototype.initialize = function(options) {
        var col, cols, getSchema, opts, recId, schemaName, schema_list, _i, _len;
        cols = (function() {
          var _i, _len, _results;
          _results = [];
          for (_i = 0, _len = inputCollections.length; _i < _len; _i++) {
            col = inputCollections[_i];
            _results.push(new ResourceCollection(col));
          }
          return _results;
        })();
        this.collections.add(cols);
        this.collectionsView = new CollectionsView({
          model: this.collections
        });
        this.collectionsView.render();
        recId = null;
        if (root.inputRecord != null) recId = root.inputRecord.id;
        this.files = new FileAttachments(null, {
          recordId: recId
        });
        this.files.on('loaded', function() {
          root.app.filesView = new FilesView({
            model: root.app.files
          });
          return root.app.filesView.render();
        });
        getSchema = function(self, schemaName, resolve) {
          var opts;
          if (resolve == null) resolve = false;
          if (schemaName === 'serviceLink' || schemaName === 'contact') {
            resolve = true;
          }
          opts = {
            url: "/metadata/schema/" + schemaName + "/",
            type: 'GET',
            data: {
              resolve: resolve
            },
            error: function(err) {
              return console.log(err);
            },
            success: function(data, status, xhr) {
              var key, value;
              self.schemas[schemaName] = data;
              if (((function() {
                var _ref, _results;
                _ref = self.schemas;
                _results = [];
                for (key in _ref) {
                  value = _ref[key];
                  _results.push(key);
                }
                return _results;
              })()).length === schema_list.length) {
                return self.trigger('schemasLoaded');
              }
            }
          };
          return $.ajax(opts);
        };
        schema_list = ['link', 'serviceLink', 'contact', 'contactInformation', 'address', 'geographicExtent', 'metadata'];
        for (_i = 0, _len = schema_list.length; _i < _len; _i++) {
          schemaName = schema_list[_i];
          getSchema(this, schemaName);
        }
        opts = {
          url: '/registry/contacts/',
          error: function(err) {
            return console.log(err);
          },
          success: function(data, status, xhr) {
            root.app.contacts = data;
            return root.app.trigger('contactsLoaded');
          }
        };
        $.ajax(opts);
        this.on('schemasLoaded', function() {
          return this.parseRecord();
        });
        this.on('contactsLoaded', function() {
          var key, value;
          $('#page-content').append(this.contactJade.content({}));
          $('#contact-selector').autocomplete({
            source: (function() {
              var _ref, _results;
              _ref = this.contacts;
              _results = [];
              for (key in _ref) {
                value = _ref[key];
                _results.push(key);
              }
              return _results;
            }).call(this)
          });
          return $('#select-contact-dialog').dialog({
            autoOpen: false,
            resizable: false,
            width: 600,
            modal: true,
            buttons: {
              'Add selected contact': function() {
                return $(this).dialog('close');
              },
              Cancel: function() {
                return $(this).dialog('close');
              }
            }
          });
        });
        $("#site-info-block").insertAfter("#map-block");
        $('.save-button, .delete-button').button();
        $('.save-button').click(this.saveRecord);
        return $('.delete-button').click(this.deleteRecord);
      };

      App.prototype.parseRecord = function() {
        var auth, author, dist, distributor, l, link, _i, _j, _k, _len, _len2, _len3, _ref, _ref2, _ref3;
        this.record.basicMetadata = new root.BasicMetadata({
          Title: this.record.get('Title'),
          Description: this.record.get('Description'),
          Published: this.record.get('Published'),
          PublicationDate: this.record.get('PublicationDate'),
          ResourceId: this.record.get('ResourceId'),
          Keywords: this.record.get('Keywords')
        });
        this.record.basicMetadata.schema = this.schemas.metadata;
        this.record.authors = new root.Contacts();
        _ref = this.record.get('Authors');
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          author = _ref[_i];
          auth = new root.Contact(author);
          auth.schema = this.schemas.contact;
          this.record.authors.add(auth);
        }
        this.record.geographicExtent = new root.GeographicExtent(this.record.get('GeographicExtent'));
        this.record.geographicExtent.schema = this.schemas.geographicExtent;
        this.record.distributors = new root.Contacts();
        _ref2 = this.record.get('Distributors');
        for (_j = 0, _len2 = _ref2.length; _j < _len2; _j++) {
          distributor = _ref2[_j];
          dist = new root.Contact(distributor);
          dist.schema = this.schemas.contact;
          this.record.distributors.add(dist);
        }
        this.record.links = new root.Links();
        _ref3 = this.record.get('Links');
        for (_k = 0, _len3 = _ref3.length; _k < _len3; _k++) {
          link = _ref3[_k];
          l = new root.Link(link);
          l.schema = link.ServiceType != null ? this.schemas.serviceLink : this.schemas.link;
          this.record.links.add(l);
        }
        this.basicMetadataView = new BasicMetadataView({
          model: this.record.basicMetadata
        });
        this.geographicExtentView = new GeographicExtentView({
          model: this.record.geographicExtent
        });
        this.basicMetadataView.render();
        this.geographicExtentView.render();
        this.authorsView = new AuthorsView({
          model: this.record.authors
        });
        this.distributorsView = new DistributorsView({
          model: this.record.distributors
        });
        this.linksView = new LinksView({
          model: this.record.links
        });
        this.authorsView.render();
        this.distributorsView.render();
        return this.linksView.render();
      };

      App.prototype.autocompleteDistributors = function() {
        var dist;
        return $('.distributors').autocomplete({
          source: (function() {
            var _i, _len, _ref, _results;
            _ref = $('.distributor-title');
            _results = [];
            for (_i = 0, _len = _ref.length; _i < _len; _i++) {
              dist = _ref[_i];
              _results.push($(dist).html());
            }
            return _results;
          })()
        });
      };

      App.prototype.saveRecord = function() {
        $('#page-content').append(root.app.confirmationJade.content({
          title: 'Save Changes?',
          message: "Are you sure you want to save your changes?"
        }));
        return $('#dialog-confirm').dialog({
          resizable: false,
          height: 160,
          modal: true,
          buttons: {
            "Save": function() {
              var opts;
              opts = {
                type: update ? 'PUT' : 'POST',
                url: update ? "/metadata/record/" + root.app.record.id + "/" : '/metadata/record/',
                contentType: 'application/json',
                parseData: false,
                data: JSON.stringify(root.app.writeOutRecord()),
                error: function(err) {
                  return console.log(err);
                },
                success: function(data, status, xhr) {
                  var id;
                  if (update) {
                    return window.location.reload();
                  } else {
                    id = xhr.getResponseHeader('Location').match(/\/(.{32})\/$/)[1];
                    return window.location.href = "/repository/resource/" + id + "/edit";
                  }
                }
              };
              $.ajax(opts);
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

      App.prototype.deleteRecord = function() {
        $('#page-content').append(root.app.confirmationJade.content({
          title: 'Delete Resource?',
          message: "Are you sure you want to completely delete this resource?"
        }));
        return $('#dialog-confirm').dialog({
          resizable: false,
          height: 160,
          modal: true,
          buttons: {
            "Delete Resource": function() {
              var opts;
              opts = {
                type: 'DELETE',
                url: "/metadata/record/" + root.app.record.id + "/",
                error: function(err) {
                  return console.log(err);
                },
                success: function(data, status, xhr) {
                  return window.location.href = '/repository/search/';
                }
              };
              $.ajax(opts);
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

      App.prototype.writeOutRecord = function() {
        var author, authors, basics, collection, collections, distributor, distributors, geo, link, links, recordJson;
        recordJson = JSON.parse(JSON.stringify(this.record));
        basics = JSON.parse(JSON.stringify(this.basicMetadataView.model));
        geo = {
          GeographicExtent: JSON.parse(JSON.stringify(this.geographicExtentView.model))
        };
        authors = {
          Authors: (function() {
            var _i, _len, _ref, _results;
            _ref = this.authorsView.model.models;
            _results = [];
            for (_i = 0, _len = _ref.length; _i < _len; _i++) {
              author = _ref[_i];
              _results.push(author.writeOut());
            }
            return _results;
          }).call(this)
        };
        distributors = {
          Distributors: (function() {
            var _i, _len, _ref, _results;
            _ref = this.distributorsView.model.models;
            _results = [];
            for (_i = 0, _len = _ref.length; _i < _len; _i++) {
              distributor = _ref[_i];
              _results.push(distributor.writeOut());
            }
            return _results;
          }).call(this)
        };
        links = {
          Links: (function() {
            var _i, _len, _ref, _results;
            _ref = this.linksView.model.models;
            _results = [];
            for (_i = 0, _len = _ref.length; _i < _len; _i++) {
              link = _ref[_i];
              _results.push(JSON.parse(JSON.stringify(link)));
            }
            return _results;
          }).call(this)
        };
        collections = {
          Collections: (function() {
            var _i, _len, _ref, _results;
            _ref = this.collectionsView.model.models;
            _results = [];
            for (_i = 0, _len = _ref.length; _i < _len; _i++) {
              collection = _ref[_i];
              _results.push((JSON.parse(JSON.stringify(collection))).id);
            }
            return _results;
          }).call(this)
        };
        return _.extend(recordJson, basics, geo, authors, distributors, links, collections);
      };

      return App;

    })(Backbone.View);
    return root.app = new App();
  });

}).call(this);
