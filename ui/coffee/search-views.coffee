root = exports ? this

class root.SearchResultView extends Backbone.View
  jade: new root.Jade '/static/templates/search-result.jade'    
  
  render: ->
    context = 
      id: @model.get('_id')
      title: @model.get('Title')
      description: "#{@model.get('Description').substring 0, 225} . . ."
      info: "#{@model.getFirstAuthorName()} - Published on #{@model.get('PublicationDate')} - Modified on #{@model.get('ModifiedDate')}"      
    @$el.append @jade.content context
    @$el.addClass('unpublished') if not @model.get('Published')    
    return @
