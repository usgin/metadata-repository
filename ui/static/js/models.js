(function() {
  var getEmptyInstance, root,
    __indexOf = Array.prototype.indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; },
    __hasProp = Object.prototype.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; };

  root = typeof exports !== "undefined" && exports !== null ? exports : this;

  getEmptyInstance = function(self, schemaName) {
    var opts;
    opts = {
      url: "/metadata/schema/" + schemaName + "/",
      type: 'GET',
      async: false,
      data: {
        emptyInstance: true
      },
      error: function(err) {
        return console.log(err);
      },
      success: function(data, status, xhr) {
        var key, keys, value;
        self.set(data);
        keys = (function() {
          var _results;
          _results = [];
          for (key in data) {
            value = data[key];
            _results.push(key);
          }
          return _results;
        })();
        if (__indexOf.call(keys, 'Published') >= 0) self.set('Published', false);
        if (__indexOf.call(keys, 'HarvestInformation') >= 0) {
          return self.unset('HarvestInformation');
        }
      }
    };
    return $.ajax(opts);
  };

  root.Resource = (function(_super) {

    __extends(Resource, _super);

    function Resource() {
      Resource.__super__.constructor.apply(this, arguments);
    }

    Resource.prototype.initialize = function(options) {
      var prop, value;
      if (((function() {
        var _results;
        _results = [];
        for (prop in options) {
          value = options[prop];
          _results.push(prop);
        }
        return _results;
      })()).length === 0) {
        return getEmptyInstance(this, 'metadata');
      }
    };

    return Resource;

  })(Backbone.Model);

  root.Resources = (function(_super) {

    __extends(Resources, _super);

    function Resources() {
      Resources.__super__.constructor.apply(this, arguments);
    }

    Resources.prototype.model = Resource;

    return Resources;

  })(Backbone.Collection);

  root.ResourceCollection = (function(_super) {

    __extends(ResourceCollection, _super);

    function ResourceCollection() {
      ResourceCollection.__super__.constructor.apply(this, arguments);
    }

    ResourceCollection.prototype.toJSON = function() {
      var result;
      return result = {
        title: this.get('title'),
        description: this.get('description'),
        can_edit: this.get('can_edit'),
        id: this.id
      };
    };

    ResourceCollection.prototype.initialize = function(options) {
      var col, rec, _i, _j, _len, _len2, _ref, _ref2;
      this.collections = new ResourceCollections();
      this.resources = new Resources();
      if ((options.child_collections != null) && options.child_collections.length > 0) {
        _ref = options.child_collections;
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          col = _ref[_i];
          this.collections.add(new ResourceCollection(col));
        }
      }
      if (options.child_resources && options.child_resources.length > 0) {
        _ref2 = options.child_resources;
        for (_j = 0, _len2 = _ref2.length; _j < _len2; _j++) {
          rec = _ref2[_j];
          this.resources.add(new Resource(rec));
        }
      }
    };

    return ResourceCollection;

  })(Backbone.Model);

  root.ResourceCollections = (function(_super) {

    __extends(ResourceCollections, _super);

    function ResourceCollections() {
      ResourceCollections.__super__.constructor.apply(this, arguments);
    }

    ResourceCollections.prototype.model = ResourceCollection;

    return ResourceCollections;

  })(Backbone.Collection);

  root.FileAttachment = (function(_super) {

    __extends(FileAttachment, _super);

    function FileAttachment() {
      FileAttachment.__super__.constructor.apply(this, arguments);
    }

    FileAttachment.prototype.idAttribute = 'filename';

    return FileAttachment;

  })(Backbone.Model);

  root.FileAttachments = (function(_super) {

    __extends(FileAttachments, _super);

    function FileAttachments() {
      FileAttachments.__super__.constructor.apply(this, arguments);
    }

    FileAttachments.prototype.model = root.FileAttachment;

    FileAttachments.prototype.initialize = function(models, options) {
      var attachments, opts;
      attachments = this;
      if (options.recordId != null) {
        opts = {
          type: 'GET',
          url: "/metadata/record/" + options.recordId + "/file/",
          error: function(err) {
            return console.log(err);
          },
          success: function(data, status, xhr) {
            var file, _i, _len;
            for (_i = 0, _len = data.length; _i < _len; _i++) {
              file = data[_i];
              attachments.add(new root.FileAttachment(file));
            }
            return attachments.trigger('loaded');
          }
        };
        return $.ajax(opts);
      } else {
        return setTimeout(function() {
          return attachments.trigger('loaded', 1);
        });
      }
    };

    return FileAttachments;

  })(Backbone.Collection);

  root.BasicMetadata = (function(_super) {

    __extends(BasicMetadata, _super);

    function BasicMetadata() {
      BasicMetadata.__super__.constructor.apply(this, arguments);
    }

    BasicMetadata.prototype.initialize = function(options) {};

    return BasicMetadata;

  })(Backbone.Model);

  root.Contact = (function(_super) {

    __extends(Contact, _super);

    function Contact() {
      Contact.__super__.constructor.apply(this, arguments);
    }

    Contact.prototype.initialize = function(options) {
      var prop, value;
      if (((function() {
        var _results;
        _results = [];
        for (prop in options) {
          value = options[prop];
          _results.push(prop);
        }
        return _results;
      })()).length === 0) {
        getEmptyInstance(this, 'contact');
      }
      this.contactInformation = new root.ContactInformation(this.get('ContactInformation'));
      return this.unset('ContactInformation');
    };

    Contact.prototype.writeOut = function() {
      var out;
      out = JSON.parse(JSON.stringify(this));
      out.ContactInformation = JSON.parse(JSON.stringify(this.contactInformation));
      out.ContactInformation.Address = JSON.parse(JSON.stringify(this.contactInformation.address));
      return out;
    };

    return Contact;

  })(Backbone.Model);

  root.ContactInformation = (function(_super) {

    __extends(ContactInformation, _super);

    function ContactInformation() {
      ContactInformation.__super__.constructor.apply(this, arguments);
    }

    ContactInformation.prototype.initialize = function(options) {
      var address;
      address = this.get('Address');
      if (address != null) {
        this.address = new root.Address(address);
        return this.unset('Address');
      }
    };

    return ContactInformation;

  })(Backbone.Model);

  root.Address = (function(_super) {

    __extends(Address, _super);

    function Address() {
      Address.__super__.constructor.apply(this, arguments);
    }

    Address.prototype.initialize = function(options) {};

    return Address;

  })(Backbone.Model);

  root.Contacts = (function(_super) {

    __extends(Contacts, _super);

    function Contacts() {
      Contacts.__super__.constructor.apply(this, arguments);
    }

    Contacts.prototype.model = root.Contact;

    return Contacts;

  })(Backbone.Collection);

  root.GeographicExtent = (function(_super) {

    __extends(GeographicExtent, _super);

    function GeographicExtent() {
      GeographicExtent.__super__.constructor.apply(this, arguments);
    }

    GeographicExtent.prototype.initialize = function(options) {};

    return GeographicExtent;

  })(Backbone.Model);

  root.Link = (function(_super) {

    __extends(Link, _super);

    function Link() {
      Link.__super__.constructor.apply(this, arguments);
    }

    Link.prototype.initialize = function(options) {
      var prop, schemaName, value;
      schemaName = options.schemaName || 'link';
      if (options.ServiceType != null) schemaName = 'serviceLink';
      this.set('schemaName', schemaName);
      if (((function() {
        var _results;
        _results = [];
        for (prop in options) {
          value = options[prop];
          if (prop !== 'schemaName') _results.push(prop);
        }
        return _results;
      })()).length === 0) {
        return getEmptyInstance(this, schemaName);
      }
    };

    Link.prototype.toJSON = function() {
      var prop, result, schema, _ref;
      result = {
        schemaName: this.get('schemaName')
      };
      _ref = this.schema.properties;
      for (prop in _ref) {
        schema = _ref[prop];
        result[prop] = this.get(prop) || null;
      }
      return result;
    };

    return Link;

  })(Backbone.Model);

  root.Links = (function(_super) {

    __extends(Links, _super);

    function Links() {
      Links.__super__.constructor.apply(this, arguments);
    }

    Links.prototype.model = root.Link;

    return Links;

  })(Backbone.Collection);

}).call(this);
