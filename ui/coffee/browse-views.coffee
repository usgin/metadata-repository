root = exports ? this

addNewCollection = (view, collectionId) ->
  $('#page-content').append(view.newCollectionJade.content { parentCollection: view.model.get 'title' })
  $('#new-collection-dialog').dialog {
    resizable: false
    width: 500
    modal: true
    buttons:
      "Create New Collection": ->
        title = $('#new-collection-title').val()
        desc = $('#new-collection-description').val()
        opts =
          type: 'POST'
          url: '/metadata/collection/'
          contentType: 'application/json'
          processData: false
          data: JSON.stringify {
            Title: title
            Description: desc
            ParentCollections: [ collectionId ]
          }
          error: (err) ->
            console.log err
          success: (data, status, xhr) ->
            loc = xhr.getResponseHeader 'Location'
            id = loc.match(/collection\/(.*)\/$/)[1]
            view.model.collections.add new root.ResourceCollection { id: id, title: title, description: desc, can_edit: true }              
            view.render()
            view.expand() if view.$el.find('.collection-content > .record-list').first().hasClass 'hidden'
            $('#new-collection-dialog').dialog 'close'
            $('#new-collection-dialog').remove()
        $.ajax opts          
      Cancel: ->
        $(this).dialog 'close'
        $(this).remove()
  }
  
getView = (viewType, id) ->
    self = @
    viewsName = "#{viewType}Views"
    childView = _.filter self[viewsName], (view) ->
      view.model.id is id
    return childView[0]
      
class root.TopCollectionView extends Backbone.View
  jade: new root.Jade '/static/templates/top-collection.jade'
  newCollectionJade: new root.Jade '/static/templates/add-new-collection.jade'
  
  tagName: 'div'
  
  className: 'collection-container'
    
  initialize: (options) ->
    @collectionId = options.model.id
    return  
     
  render: ->
    @$el.empty()
    @$el.append @jade.content @model.toJSON()
    ul = @$el.find('.collection-content > .record-list').first()
    thisView = @
    @collectionViews = []
    @resourceViews = []
    @model.collections.forEach (collection) ->
      childView = new root.ChildCollectionView { model: collection, parent: thisView }
      thisView.collectionViews.push childView
      ul.append childView.render().el
    @model.resources.forEach (resource) ->
      resourceView = new root.ChildResourceView { model: resource, parent: thisView }
      this.resourceViews.push resourceView
      ul.append resourceView.render().el    
    return @
    
  events:
    'click .expand:first': 'expand'
    'click .addCollection:first': 'addCollection'
    'click .addRecord:first': 'addRecord'    
    
  expand: ->
    ul = @$el.find('.collection-content > .record-list').first()
    tri = @$el.find('.collection-list-expand').first()
    if ul.hasClass('hidden')
      ul.removeClass('hidden')
      tri.removeClass('ui-icon-triangle-1-e')
      tri.addClass('ui-icon-triangle-1-s')
    else
      ul.addClass('hidden')
      tri.removeClass('ui-icon-triangle-1-s')
      tri.addClass('ui-icon-triangle-1-e')
      
  addCollection: (event) ->
    addNewCollection @, @collectionId
    
  addRecord: (event) ->
    window.location.href = "/repository/collection/#{@collectionId}/resource/new"    
    
  getView: getView
       
class root.ChildCollectionView extends Backbone.View
  jade: new root.Jade '/static/templates/child-collection.jade'
  newCollectionJade: new root.Jade '/static/templates/add-new-collection.jade'
  confirmationJade: new root.Jade '/static/templates/confirmation-dialog.jade'
  
  tagName: 'li'
  
  className: 'record-container collection-item collection-container'
    
  initialize: (options) ->
    @parentView = options.parent if options.parent?
    @collectionId = options.model.id
    return
    
  render: ->
    @$el.empty()
    @$el.append @jade.content @model.toJSON()
    thisView = @
    @renderChildren()
    
  populateCollection: (event) -> 
    id = $(event.currentTarget).attr('id').split('-container')[0]
    self = @    
    opts =
      type: 'GET'
      dataType: 'json'
      url: "/repository/collection/#{ id }.json"
      success: (response, status, xhr) ->
        ul = $(event.currentTarget).next()        
        self.model = new ResourceCollection response
        childView = self.parentView.getView 'collection', response.id        
        childView.renderChildren()
        childView.$el.find("##{id}-container").removeClass 'not-populated'
        return 
    $.ajax opts
        
  renderChildren: ->
    thisView = @
    ul = @$el.children('ul').first()
    @collectionViews = []
    @resourceViews = []
    @model.collections.forEach (collection) ->
      childView = new root.ChildCollectionView { model: collection, parent: thisView }
      thisView.collectionViews.push childView
      ul.append childView.render().el
    @model.resources.forEach (resource) ->
      resourceView = new root.ChildResourceView { model: resource, parent: thisView }
      thisView.resourceViews.push resourceView
      ul.append resourceView.render().el
    return @
    
  events: ->
    populateLink = "click ##{@model.id}-container.not-populated"
    events = {
      'click .expand:first': 'expand'      
      'click .addCollection:first': 'addCollection'
      'click .addRecord:first': 'addRecord'
      'click .deleteCollection:first': 'deleteCollection'
    }
    events[populateLink] = 'populateCollection'
    return events
    
  expand: (event)->
    ul = @$el.find('ul.record-list').first()
    tri = @$el.find('.collection-list-expand').first()
    if ul.hasClass('hidden')
      ul.removeClass('hidden')
      tri.removeClass('ui-icon-triangle-1-e')
      tri.addClass('ui-icon-triangle-1-s')
    else
      ul.addClass('hidden')
      tri.removeClass('ui-icon-triangle-1-s')
      tri.addClass('ui-icon-triangle-1-e')
          
  addCollection: (event) ->
    addNewCollection @, @collectionId
    
  addRecord: (event) ->
    window.location.href = "/repository/collection/#{@collectionId}/resource/new"
    
  deleteCollection: (event) ->
    console.log "remove the collection #{@collectionId} from #{@parentView.collectionId}"
    view = @
    $('#page-content').append(view.confirmationJade.content { title: 'Remove Child Collection?',  message: 'Are you sure you want to remove this collection from its parent?' })
    $('#dialog-confirm').dialog {
      resizable: false
      width: 400
      modal: true
      buttons:
        "Remove": ->
          # Adjust the collection's ParentCollection attribute
          getOpts =
            type: 'GET'
            url: "/metadata/collection/#{view.collectionId}/"
            error: (err) ->
              console.log err
            success: (data, status, xhr) ->
              data.ParentCollections = ( col for col in data.ParentCollections when col isnt view.parentView.collectionId )
              putOpts =
                type: 'PUT'
                url: "/metadata/collection/#{view.collectionId}/"
                contentType: 'application/json'
                processData: false
                data: JSON.stringify data
                error: (err) ->
                  console.log err
                success: (data, status, xhr) ->
                  console.log status
              $.ajax putOpts
          $.ajax getOpts
          
          # Adjust the UI
          view.parentView.model.collections.remove view.model
          view.parentView.render()
          view.parentView.expand()
          $(this).dialog 'close'
          $(this).remove()
        Cancel: ->
          $(this).dialog 'close'
          $(this).remove()
    }
    
  getView: getView
  
class root.ChildResourceView extends Backbone.View 
  jade: new root.Jade '/static/templates/child-resource.jade'
  confirmationJade: new root.Jade '/static/templates/confirmation-dialog.jade'
  
  tagName: 'li'
  
  className: 'record-container'
    
  initialize: (options) ->
    @parentView = options.parent if options.parent?
    @resourceId = options.model.id
    return
    
  render: ->
    @$el.append @jade.content @model.toJSON()
    return @
    
  events:
    'click .deleteRecord:first': 'deleteRecord'
    
  deleteRecord: ->
    console.log "Remove record #{@resourceId} from #{@parentView.collectionId}"
    view = @
    $('#page-content').append(view.confirmationJade.content { title: 'Remove Child Resource?',  message: 'Are you sure you want to remove this resource from its collection?' })
    $('#dialog-confirm').dialog {
      resizable: false
      width: 400
      modal: true
      buttons:
        "Remove": ->
          # Adjust the resource's Collections attribute
          getOpts =
            type: 'GET'
            url: "/metadata/record/#{view.resourceId}/"
            error: (err) ->
              console.log err
            success: (data, status, xhr) ->
              data.Collections = ( col for col in data.Collections when col isnt view.parentView.collectionId )
              putOpts =
                type: 'PUT'
                url: "/metadata/record/#{view.resourceId}/"
                contentType: 'application/json'
                processData: false
                data: JSON.stringify data
                error: (err) ->
                  console.log err
                success: (data, status, xhr) ->
                  console.log status
              $.ajax putOpts
          $.ajax getOpts
          
          # Adjust the UI
          view.parentView.model.resources.remove view.model
          view.parentView.render()
          view.parentView.expand()
          $(this).dialog 'close'
          $(this).remove()
        Cancel: ->
          $(this).dialog 'close'
          $(this).remove()
    }
