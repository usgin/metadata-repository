root = exports ? this

$(document).ready ->
  class CollectionBrowser extends Backbone.View
    topCollections: new root.ResourceCollections()
    topViews: []
    el: $ '#collection-list'
    initialize: ->
      @topCollections.add new root.ResourceCollection col for col in root.collections    
      @renderCollections()
      return
    
    render: ->
      return @
      
    renderCollections: ->
      that = @
      @topCollections.forEach (collection) ->
        topView = new root.TopCollectionView { model: collection }        
        that.$el.append topView.render().el
        return
      return
    
  root.application = new CollectionBrowser()
  return