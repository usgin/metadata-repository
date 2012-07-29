root = exports ? this
jade = require 'jade'

class root.Jade
  constructor: (@url) ->
    that = @
    options =
      url: @url
      async: false
      success: (result) ->
        that.jadeFn = jade.compile(result)
        return
    $.ajax options
  content: (context) ->
    return @jadeFn context
