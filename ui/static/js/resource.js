(function() {
  var root;

  root = typeof exports !== "undefined" && exports !== null ? exports : this;

  $(document).ready(function() {
    $("#site-info-block").insertAfter("#formal-metadata-block");
    return $("#edit-button").button();
  });

}).call(this);
