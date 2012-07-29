(function() {
  var collapseFieldsets, resizeInputs, root,
    __hasProp = Object.prototype.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; };

  root = typeof exports !== "undefined" && exports !== null ? exports : this;

  root.CollectionsView = (function(_super) {

    __extends(CollectionsView, _super);

    function CollectionsView() {
      CollectionsView.__super__.constructor.apply(this, arguments);
    }

    CollectionsView.prototype.jade = new root.Jade('/static/templates/edit-collection.jade');

    CollectionsView.prototype.confirmation = new root.Jade('/static/templates/confirmation-dialog.jade');

    CollectionsView.prototype.newCollection = new root.Jade('/static/templates/new-collection-dialog.jade');

    CollectionsView.prototype.tagName = 'ul';

    CollectionsView.prototype.id = 'collections-current-list';

    CollectionsView.prototype.className = 'menu';

    CollectionsView.prototype.parentId = '#collections-content';

    CollectionsView.prototype.initialize = function(options) {};

    CollectionsView.prototype.render = function() {
      var col, _i, _len, _ref;
      this.$el.empty();
      _ref = this.model.models;
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        col = _ref[_i];
        this.$el.append(this.jade.content(col.toJSON()));
      }
      this.$el.append('<li id="add-to-collection" class="link-ish">Add to a new Collection</li>');
      $(this.parentId).append(this.$el);
      return this;
    };

    CollectionsView.prototype.events = {
      'click #add-to-collection': 'addToCollection',
      'click .deleteCollection': 'deleteCollection'
    };

    CollectionsView.prototype.addToCollection = function() {
      var col;
      $('#page-content').append(this.newCollection.content({}));
      $('#new-collection-selector').autocomplete({
        source: (function() {
          var _i, _len, _ref, _results;
          _ref = root.allCollections;
          _results = [];
          for (_i = 0, _len = _ref.length; _i < _len; _i++) {
            col = _ref[_i];
            _results.push({
              id: col.id,
              value: col.title
            });
          }
          return _results;
        })(),
        select: function(evt, ui) {
          $('#new-selected-collection').val(ui.item.id);
          $(this).val(ui.item.value);
          return false;
        }
      });
      return $('#add-collection-dialog').dialog({
        resizable: false,
        width: 500,
        modal: true,
        buttons: {
          "Add to selected collection": function() {
            var cols, id, opts, updateUi;
            id = $('#new-selected-collection').val();
            updateUi = function() {
              col = new ResourceCollection({
                id: id,
                title: $('#new-collection-selector').val(),
                can_edit: true
              });
              root.app.collectionsView.model.add(col);
              return root.app.collectionsView.render();
            };
            if (update) {
              cols = root.app.record.get('Collections');
              cols.push(id);
              root.app.record.set('Collections', cols);
              opts = {
                type: 'PUT',
                url: "/metadata/record/" + root.app.record.id + "/",
                processDate: false,
                contentType: 'application/json',
                data: JSON.stringify(root.app.record.toJSON()),
                error: function(err) {
                  return console.log(err);
                },
                success: function(response) {
                  updateUi();
                  $('#add-collection-dialog').dialog('close');
                  return $('#add-collection-dialog').remove();
                }
              };
              return $.ajax(opts);
            } else {
              updateUi();
              $(this).dialog('close');
              return $(this).remove();
            }
          },
          Cancel: function() {
            $(this).dialog('close');
            return $(this).remove();
          }
        }
      });
    };

    CollectionsView.prototype.deleteCollection = function(evt) {
      var id, updateUi;
      id = evt.currentTarget.id.split('-')[0];
      $('#page-content').append(this.confirmation.content({
        title: 'Remove from collection?',
        message: "Remove this record from '" + ($(evt.currentTarget).parent().next().text()) + "'?"
      }));
      updateUi = function() {
        var col;
        col = root.app.collectionsView.model.get(id);
        root.app.collectionsView.model.remove(col);
        return root.app.collectionsView.render();
      };
      return $('#dialog-confirm').dialog({
        resizable: false,
        height: 160,
        modal: true,
        buttons: {
          "Remove": function() {
            var col, cols, opts;
            if (update) {
              cols = root.app.record.get('Collections');
              root.app.record.set('Collections', (function() {
                var _i, _len, _results;
                _results = [];
                for (_i = 0, _len = cols.length; _i < _len; _i++) {
                  col = cols[_i];
                  if (col !== id) _results.push(col);
                }
                return _results;
              })());
              opts = {
                type: 'PUT',
                url: "/metadata/record/" + root.app.record.id + "/",
                processData: false,
                contentType: 'application/json',
                data: JSON.stringify(root.app.record.toJSON()),
                error: function(err) {
                  return console.log(err);
                },
                success: function(response) {
                  return updateUi();
                }
              };
              $.ajax(opts);
            } else {
              updateUi();
            }
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

    return CollectionsView;

  })(Backbone.View);

  root.FilesView = (function(_super) {

    __extends(FilesView, _super);

    function FilesView() {
      FilesView.__super__.constructor.apply(this, arguments);
    }

    FilesView.prototype.fileJade = new root.Jade('/static/templates/edit-file.jade');

    FilesView.prototype.confirmationJade = new root.Jade('/static/templates/confirmation-dialog.jade');

    FilesView.prototype.newFileJade = new root.Jade('/static/templates/file-upload-dialog.jade');

    FilesView.prototype.tagName = 'ul';

    FilesView.prototype.className = 'menu';

    FilesView.prototype.id = 'file-attachments-list';

    FilesView.prototype.parentId = '#file-attachment-content';

    FilesView.prototype.render = function() {
      var file, _i, _len, _ref;
      this.$el.empty();
      _ref = this.model.models;
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        file = _ref[_i];
        this.$el.append(this.fileJade.content(file.toJSON()));
      }
      if (update) {
        this.$el.append('<li id="add-new-file" class="link-ish">Attach a new file</li>');
      } else {
        this.$el.append('<li id="no-files-yet">Please save your record before attaching files</li>');
      }
      $(this.parentId).append(this.$el);
      return this;
    };

    FilesView.prototype.events = {
      'click #add-new-file': 'addFile',
      'click .deleteFile': 'deleteFile'
    };

    FilesView.prototype.addFile = function() {
      $('#page-content').append(this.newFileJade.content({
        id: root.app.record.id
      }));
      return $('#new-file-dialog').dialog({
        resizable: false,
        width: 400,
        modal: true,
        buttons: {
          "Upload File": function() {
            $('#new-file-form').ajaxForm();
            return $('#new-file-form').ajaxSubmit({
              success: function(data, status, xhr) {
                var f, filename, loc;
                loc = xhr.getResponseHeader('Location');
                filename = loc.split('/').pop();
                f = new FileAttachment({
                  filename: filename,
                  location: loc
                });
                root.app.filesView.model.add(f);
                root.app.filesView.render();
                root.app.linksView.addLink(loc, filename);
                $('#new-file-dialog').dialog('close');
                return $('#new-file-dialog').remove();
              }
            });
          },
          Cancel: function() {
            $(this).dialog('close');
            return $(this).remove();
          }
        }
      });
    };

    FilesView.prototype.deleteFile = function(evt) {
      var id;
      id = evt.currentTarget.id.split('-')[0];
      $('#page-content').append(this.confirmationJade.content({
        title: 'Delete File?',
        message: "Delete " + id + "?"
      }));
      return $('#dialog-confirm').dialog({
        resizable: false,
        height: 160,
        modal: true,
        buttons: {
          "Remove": function() {
            var opts;
            opts = {
              type: 'DELETE',
              url: "/metadata/record/" + root.app.record.id + "/file/" + id,
              error: function(err) {
                return console.log(err);
              },
              success: function(data, status, xhr) {
                var f;
                f = root.app.filesView.model.get(id);
                root.app.filesView.model.remove(f);
                return root.app.filesView.render();
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

    return FilesView;

  })(Backbone.View);

  root.AuthorsView = (function(_super) {

    __extends(AuthorsView, _super);

    function AuthorsView() {
      AuthorsView.__super__.constructor.apply(this, arguments);
    }

    AuthorsView.prototype.id = 'authors';

    AuthorsView.prototype.className = 'required array-container';

    AuthorsView.prototype.jade = new root.Jade('/static/templates/edit-authors.jade');

    AuthorsView.prototype.parentId = '#resource-container';

    AuthorsView.prototype.render = function() {
      var model, _i, _len, _ref;
      this.$el.empty();
      this.$el.append(this.jade.content({}));
      this.$el.insertAfter($('#geographic-extent'));
      _ref = this.model.models;
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        model = _ref[_i];
        (new root.AuthorView({
          model: model
        })).render();
      }
      return this;
    };

    AuthorsView.prototype.events = {
      'click legend:first > span': 'collapse',
      'click .add-button': 'newAuthor',
      'click .add-contact-button': 'addContact'
    };

    AuthorsView.prototype.collapse = function(evt) {
      return collapseFieldsets(evt.target);
    };

    AuthorsView.prototype.newAuthor = function() {
      var authorView, newAuthor;
      newAuthor = new root.Contact({});
      this.model.add(newAuthor);
      authorView = new root.AuthorView({
        model: newAuthor
      });
      return authorView.render();
    };

    AuthorsView.prototype.addContact = function() {
      var dialog;
      dialog = $('#select-contact-dialog');
      dialog.unbind();
      dialog.bind('dialogclose', function(evt, ui) {
        var authorView, contact, newAuthor;
        contact = root.app.contacts[$('#contact-selector').val()];
        newAuthor = new root.Contact(contact);
        root.app.authorsView.model.add(newAuthor);
        authorView = new root.AuthorView({
          model: newAuthor
        });
        return authorView.render();
      });
      return dialog.dialog('open');
    };

    return AuthorsView;

  })(Backbone.View);

  root.DistributorsView = (function(_super) {

    __extends(DistributorsView, _super);

    function DistributorsView() {
      DistributorsView.__super__.constructor.apply(this, arguments);
    }

    DistributorsView.prototype.id = 'distributors';

    DistributorsView.prototype.className = 'required array-container';

    DistributorsView.prototype.jade = new root.Jade('/static/templates/edit-distributors.jade');

    DistributorsView.prototype.parentId = '#resource-container';

    DistributorsView.prototype.render = function() {
      var model, _i, _len, _ref;
      this.$el.empty();
      this.$el.append(this.jade.content({}));
      this.$el.insertAfter($('#authors'));
      _ref = this.model.models;
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        model = _ref[_i];
        (new root.DistributorView({
          model: model
        })).render();
      }
      root.app.autocompleteDistributors();
      return this;
    };

    DistributorsView.prototype.events = {
      'click legend:first > span': 'collapse',
      'click .add-button': 'newDistributor',
      'click .add-contact-button': 'addContact'
    };

    DistributorsView.prototype.collapse = function(evt) {
      return collapseFieldsets(evt.target);
    };

    DistributorsView.prototype.newDistributor = function() {
      var distView, newDist;
      newDist = new root.Contact({});
      this.model.add(newDist);
      distView = new root.DistributorView({
        model: newDist
      });
      return distView.render();
    };

    DistributorsView.prototype.addContact = function() {
      var dialog;
      dialog = $('#select-contact-dialog');
      dialog.unbind();
      dialog.bind('dialogclose', function(evt, ui) {
        var contact, distView, newDist;
        contact = root.app.contacts[$('#contact-selector').val()];
        newDist = new root.Contact(contact);
        root.app.distributorsView.model.add(newDist);
        distView = new root.DistributorView({
          model: newDist
        });
        return distView.render();
      });
      return dialog.dialog('open');
    };

    return DistributorsView;

  })(Backbone.View);

  root.LinksView = (function(_super) {

    __extends(LinksView, _super);

    function LinksView() {
      LinksView.__super__.constructor.apply(this, arguments);
    }

    LinksView.prototype.id = 'links';

    LinksView.prototype.className = 'required array-container';

    LinksView.prototype.jade = new root.Jade('/static/templates/edit-links.jade');

    LinksView.prototype.parentId = '#resource-container';

    LinksView.prototype.render = function() {
      var model, _i, _len, _ref;
      this.$el.empty();
      this.$el.append(this.jade.content({}));
      this.$el.insertAfter($('#distributors'));
      _ref = this.model.models;
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        model = _ref[_i];
        (new root.LinkView({
          model: model
        })).render();
      }
      root.app.autocompleteDistributors();
      return this;
    };

    LinksView.prototype.events = {
      'click legend:first > span': 'collapse',
      'click .add-file-button': 'addLink',
      'click .add-service-button': 'addServiceLink'
    };

    LinksView.prototype.collapse = function(evt) {
      return collapseFieldsets(evt.target);
    };

    LinksView.prototype.addLink = function(url, name) {
      var link, linkOpts;
      if (url == null) url = null;
      if (name == null) name = null;
      linkOpts = {
        schemaName: 'link'
      };
      if (url != null) linkOpts.URL = url;
      if (url != null) linkOpts.Name = name;
      link = new root.Link(linkOpts);
      link.schema = root.app.schemas.link;
      root.app.linksView.model.add(link);
      return root.app.linksView.render();
    };

    LinksView.prototype.addServiceLink = function() {
      var link;
      link = new root.Link({
        schemaName: 'serviceLink'
      });
      link.schema = root.app.schemas.serviceLink;
      root.app.linksView.model.add(link);
      return root.app.linksView.render();
    };

    return LinksView;

  })(Backbone.View);

  resizeInputs = function(index, ele) {
    var additional, border, eleWidth, spanWidth;
    ele = $(ele);
    eleWidth = ele.innerWidth();
    border = ele.hasClass('required') ? 3 : 5;
    spanWidth = ele.children('span').length > 0 ? ele.children('span').width() - border : 0;
    additional = ele.children('.remove-button').length > 0 ? 5 : 21;
    ele.children('input, select').width(eleWidth - spanWidth - additional);
  };

  collapseFieldsets = function(target) {
    var ele, fieldset, isCollapsed;
    ele = $(target);
    ele.parent().toggleClass('collapsed');
    isCollapsed = ele.parent().hasClass('collapsed');
    fieldset = ele.parent().parent();
    if (isCollapsed) {
      fieldset.css('height', 45);
    } else {
      fieldset.css('height', 'auto');
    }
    return fieldset.children().not('legend').each(function(index, ele) {
      if (isCollapsed) {
        return $(this).addClass('hidden');
      } else {
        return $(this).removeClass('hidden');
      }
    });
  };

  root.BasicMetadataView = (function(_super) {

    __extends(BasicMetadataView, _super);

    function BasicMetadataView() {
      BasicMetadataView.__super__.constructor.apply(this, arguments);
    }

    BasicMetadataView.prototype.id = 'basic-metadata';

    BasicMetadataView.prototype.jade = new root.Jade('/static/templates/edit-basic-metadata.jade');

    BasicMetadataView.prototype.parentId = '#resource-container';

    BasicMetadataView.prototype.render = function() {
      this.$el.empty();
      this.$el.append(this.jade.content(this.model.toJSON()));
      $(this.parentId).prepend(this.$el);
      this.$el.find(".key-value").each(resizeInputs);
      this.$el.find('input[attr="PublicationDate"]').datepicker({
        dateFormat: "yy-mm-ddT00:00:00",
        changeMonth: true,
        changeYear: true
      });
      return this;
    };

    BasicMetadataView.prototype.events = {
      'click legend > span': 'collapse',
      'change input, textarea': 'changeAttribute',
      'click .add-button': 'newKeyword',
      'click .remove-button': 'removeKeyword'
    };

    BasicMetadataView.prototype.collapse = function(evt) {
      return collapseFieldsets(evt.target);
    };

    BasicMetadataView.prototype.changeAttribute = function(evt) {
      var attr, ele, input, value;
      ele = $(evt.target);
      attr = ele.attr('attr');
      value = attr === 'Published' ? ele.is(':checked') : ele.val();
      if (attr === 'Keyword') {
        attr = 'Keywords';
        value = (function() {
          var _i, _len, _ref, _results;
          _ref = $('#keywords-list').find('input');
          _results = [];
          for (_i = 0, _len = _ref.length; _i < _len; _i++) {
            input = _ref[_i];
            _results.push($(input).val());
          }
          return _results;
        })();
      }
      this.model.set(attr, value);
    };

    BasicMetadataView.prototype.newKeyword = function() {
      var keys;
      keys = this.model.get('Keywords');
      keys.splice(0, 0, '');
      this.model.set('Keywords', keys);
      return this.render();
    };

    BasicMetadataView.prototype.removeKeyword = function(evt) {
      var key, keys, rem;
      rem = $(evt.target).siblings('input').val();
      keys = this.model.get('Keywords');
      this.model.set('Keywords', (function() {
        var _i, _len, _results;
        _results = [];
        for (_i = 0, _len = keys.length; _i < _len; _i++) {
          key = keys[_i];
          if (key !== rem) _results.push(key);
        }
        return _results;
      })());
      return this.render();
    };

    return BasicMetadataView;

  })(Backbone.View);

  root.ContactView = (function(_super) {

    __extends(ContactView, _super);

    function ContactView() {
      ContactView.__super__.constructor.apply(this, arguments);
    }

    ContactView.prototype.tagName = 'li';

    ContactView.prototype.className = 'object-container';

    ContactView.prototype.contactJade = new root.Jade('/static/templates/edit-contact.jade');

    ContactView.prototype.contactInfoJade = new root.Jade('/static/templates/edit-contact-information.jade');

    ContactView.prototype.addressJade = new root.Jade('/static/templates/edit-address.jade');

    ContactView.prototype.confirmationJade = new root.Jade('/static/templates/confirmation-dialog.jade');

    ContactView.prototype.render = function() {
      this.$el.append(this.contactJade.content(this.model.toJSON()));
      this.$el.find('.contact-information').append(this.contactInfoJade.content(this.model.contactInformation.toJSON()));
      this.$el.find('.address').append(this.addressJade.content(this.model.contactInformation.address.toJSON()));
      $(this.parentId).prepend(this.$el);
      this.$el.find(".key-value").each(resizeInputs);
      if (this.parentId === '#distributors-list') {
        this.$el.find('legend:first > span').addClass('distributor-title');
      }
      return this;
    };

    ContactView.prototype.events = {
      'click legend > span': 'collapse',
      'click .remove-array-item-button': 'removeContact',
      'change input': 'changeAttribute'
    };

    ContactView.prototype.collapse = function(evt) {
      return collapseFieldsets(evt.target);
    };

    ContactView.prototype.removeContact = function(evt) {
      var self;
      self = this;
      $('#page-content').append(this.confirmationJade.content({
        title: 'Remove Contact?',
        message: "Are you sure you want to remove this contact?"
      }));
      return $('#dialog-confirm').dialog({
        resizable: false,
        height: 160,
        modal: true,
        buttons: {
          "Remove": function() {
            var contactsView;
            contactsView = self.parentId === '#authors-list' ? root.app.authorsView : root.app.distributorsView;
            contactsView.model.remove(self.model);
            contactsView.render();
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

    ContactView.prototype.changeAttribute = function(evt) {
      var attr, ele, model, value;
      ele = $(evt.target);
      attr = ele.attr('attr');
      value = ele.val();
      model = this.model;
      if (attr === 'Phone' || attr === 'email') {
        model = this.model.contactInformation;
      }
      if (attr === 'Street' || attr === 'City' || attr === 'State' || attr === 'Zip') {
        model = this.model.contactInformation.address;
      }
      model.set(attr, value);
      if (attr === 'Name' || attr === 'OrganizationName') {
        this.adjustContactTitle();
      }
      if (this.parentId === '#distributors-list') {
        root.app.autocompleteDistributors();
      }
    };

    ContactView.prototype.adjustContactTitle = function() {
      var linkDist, name, orgName, val, _i, _len, _ref;
      name = this.model.get('Name');
      orgName = this.model.get('OrganizationName');
      val = (name === '' || name === 'No Name Was Given') && (orgName != null) ? orgName : name;
      if (this.parentId === '#distributors-list') {
        _ref = $('.distributors');
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          linkDist = _ref[_i];
          if ($(linkDist).val() === this.$el.find('legend:first > span').html()) {
            $(linkDist).val(val);
          }
        }
      }
      return this.$el.find('legend:first > span').html(val);
    };

    return ContactView;

  })(Backbone.View);

  root.AuthorView = (function(_super) {

    __extends(AuthorView, _super);

    function AuthorView() {
      AuthorView.__super__.constructor.apply(this, arguments);
    }

    AuthorView.prototype.parentId = '#authors-list';

    return AuthorView;

  })(root.ContactView);

  root.DistributorView = (function(_super) {

    __extends(DistributorView, _super);

    function DistributorView() {
      DistributorView.__super__.constructor.apply(this, arguments);
    }

    DistributorView.prototype.parentId = '#distributors-list';

    return DistributorView;

  })(root.ContactView);

  root.GeographicExtentView = (function(_super) {

    __extends(GeographicExtentView, _super);

    function GeographicExtentView() {
      GeographicExtentView.__super__.constructor.apply(this, arguments);
    }

    GeographicExtentView.prototype.id = 'geographic-extent';

    GeographicExtentView.prototype.className = 'required object-container';

    GeographicExtentView.prototype.parentId = '#resource-container';

    GeographicExtentView.prototype.jade = new root.Jade('/static/templates/edit-geographic-extent.jade');

    GeographicExtentView.prototype.render = function() {
      this.$el.empty();
      this.$el.append(this.jade.content(this.model.toJSON()));
      this.$el.insertAfter($('#basic-metadata'));
      this.$el.find(".key-value").each(resizeInputs);
      return this;
    };

    GeographicExtentView.prototype.events = {
      'click legend > span': 'collapse',
      'change input': 'changeAttribute'
    };

    GeographicExtentView.prototype.collapse = function(evt) {
      return collapseFieldsets(evt.target);
    };

    GeographicExtentView.prototype.changeAttribute = function(evt) {
      var attr, ele;
      ele = $(evt.target);
      attr = ele.attr('attr');
      return this.model.set(attr, parseInt(ele.val()));
    };

    return GeographicExtentView;

  })(Backbone.View);

  root.LinkView = (function(_super) {

    __extends(LinkView, _super);

    function LinkView() {
      LinkView.__super__.constructor.apply(this, arguments);
    }

    LinkView.prototype.parentId = '#links-list';

    LinkView.prototype.tagName = 'li';

    LinkView.prototype.className = 'object-container';

    LinkView.prototype.jade = new root.Jade('/static/templates/edit-link.jade');

    LinkView.prototype.confirmationJade = new root.Jade('/static/templates/confirmation-dialog.jade');

    LinkView.prototype.render = function() {
      this.$el.append(this.jade.content(this.model.toJSON()));
      $(this.parentId).prepend(this.$el);
      this.$el.find(".key-value").each(resizeInputs);
      return this;
    };

    LinkView.prototype.events = {
      'click legend > span': 'collapse',
      'click .remove-array-item-button': 'removeLink',
      'change input, select': 'changeAttribute'
    };

    LinkView.prototype.collapse = function(evt) {
      return collapseFieldsets(evt.target);
    };

    LinkView.prototype.removeLink = function(evt) {
      var self;
      self = this;
      $('#page-content').append(this.confirmationJade.content({
        title: 'Remove Link?',
        message: "Are you sure you want to remove this link?"
      }));
      return $('#dialog-confirm').dialog({
        resizable: false,
        height: 160,
        modal: true,
        buttons: {
          "Remove": function() {
            root.app.linksView.model.remove(self.model);
            root.app.linksView.render();
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

    LinkView.prototype.changeAttribute = function(evt) {
      var attr, ele;
      ele = $(evt.target);
      attr = ele.attr('attr');
      this.model.set(attr, ele.val());
      if (attr === 'Name' || attr === 'URL' || attr === 'ServiceType') {
        return this.adjustLinkTitle();
      }
    };

    LinkView.prototype.adjustLinkTitle = function() {
      var name, st, url, val;
      st = this.model.get('ServiceType');
      url = this.model.get('URL');
      name = this.model.get('Name');
      val = url;
      if ((st != null) && st !== '') val = st;
      if ((name != null) && name !== '') val = name;
      return this.$el.find('legend span').html(val);
    };

    return LinkView;

  })(Backbone.View);

}).call(this);
