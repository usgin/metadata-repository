(function() {
  var jade, root;

  root = typeof exports !== "undefined" && exports !== null ? exports : this;

  jade = require('jade');

  root.Jade = (function() {

    function Jade(url) {
      var options, that;
      this.url = url;
      that = this;
      options = {
        url: this.url,
        async: false,
        success: function(result) {
          that.jadeFn = jade.compile(result);
        }
      };
      $.ajax(options);
    }

    Jade.prototype.content = function(context) {
      return this.jadeFn(context);
    };

    return Jade;

  })();

}).call(this);
