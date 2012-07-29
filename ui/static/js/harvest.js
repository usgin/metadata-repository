(function() {
  var root,
    __hasProp = Object.prototype.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; };

  root = typeof exports !== "undefined" && exports !== null ? exports : this;

  $(document).ready(function() {
    var HarvestApplication;
    HarvestApplication = (function(_super) {

      __extends(HarvestApplication, _super);

      function HarvestApplication() {
        HarvestApplication.__super__.constructor.apply(this, arguments);
      }

      HarvestApplication.prototype.jade = new root.Jade('/static/templates/harvest-application.jade');

      HarvestApplication.prototype.responseJade = new root.Jade('/static/templates/harvest-response.jade');

      HarvestApplication.prototype.el = $('#harvest-button-container');

      HarvestApplication.prototype.initialize = function(options) {
        var opts;
        this.render();
        opts = {
          source: root.collections,
          select: function(event, ui) {
            $('#selected-collection').val(ui.item.id);
            $(this).val(ui.item.value);
            return false;
          },
          change: function(event, ui) {
            if (!(ui.item != null)) return $('#selected-collection').val('');
          }
        };
        $('#collection-selector').autocomplete(opts);
      };

      HarvestApplication.prototype.render = function() {
        this.$el.append(this.jade.content({}));
        return this;
      };

      HarvestApplication.prototype.events = {
        'click': 'doHarvest'
      };

      HarvestApplication.prototype.doHarvest = function() {
        var opts, postBody;
        postBody = {
          recordUrl: $('#input-url').val(),
          inputFormat: $('input[name=harvestFormat]:checked').val(),
          destinationCollections: [$('#selected-collection').val()]
        };
        opts = {
          type: 'POST',
          contentType: 'application/json',
          url: '/metadata/harvest/',
          data: JSON.stringify(postBody),
          processData: false,
          error: function(err) {
            return console.log(err);
          },
          success: function(response) {
            var ids, loc;
            ids = (function() {
              var _i, _len, _results;
              _results = [];
              for (_i = 0, _len = response.length; _i < _len; _i++) {
                loc = response[_i];
                _results.push(loc.substring(17, loc.length - 1));
              }
              return _results;
            })();
            return $('#page-content').empty().append(root.app.responseJade.content({
              newResources: ids
            }));
          }
        };
        return $.ajax(opts);
      };

      return HarvestApplication;

    })(Backbone.View);
    return root.app = new HarvestApplication();
  });

}).call(this);
