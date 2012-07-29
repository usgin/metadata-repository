root = exports ? this

$(document).ready ->
  # Put the site-info block at the bottom of the sidebar
  $("#site-info-block").insertAfter("#formal-metadata-block");
  # jQuery-UI: Change edit link into a button
  $("#edit-button").button();
