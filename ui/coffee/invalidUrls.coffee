$(document).ready ->
  $("#refresh").bind "click", ->
    btn = $(this)
    btn.addClass "thinking"
    btn.removeClass "ready"
    btn.html "...WORKING..."
    $.ajax
      type: "GET"
      url: "/repository/invalidUrls?refresh=true"
      success: (response, status, xhr) ->
        if response.returncode is 0
          window.location.reload()
        else
          btn.html "...ERROR..."
        btn.removeClass "thinking"

      error: (error) ->
        btn.removeClass "thinking"
        btn.html "...ERROR..."

    btn.unbind "click"