root = exports ? this

$(document).ready ->
  
  class HarvestApplication extends Backbone.View
    jade: new root.Jade '/static/templates/harvest-application.jade'
    
    responseJade: new root.Jade '/static/templates/harvest-response.jade'
    
    el: $ '#harvest-button-container'
    
    initialize: (options) ->
      @render()
      
      # Setup the Collection Name autocomplete
      opts =
        source: root.collections
        select: (event, ui) ->
          $('#selected-collection').val ui.item.id
          $(this).val ui.item.value
          return false
        change: (event, ui) ->
          if not ui.item?
            $('#selected-collection').val ''
      $('#collection-selector').autocomplete opts
      return 
      
    render: ->
      @$el.append @jade.content {}
      return @
      
    events:
      'click': 'doHarvest'
      
    doHarvest: ->
      postBody =
        recordUrl: $('#input-url').val()
        inputFormat: $('input[name=harvestFormat]:checked').val()
        destinationCollections: [ $('#selected-collection').val() ]
      opts =
        type: 'POST'
        contentType: 'application/json'
        url: '/metadata/harvest/'
        data: JSON.stringify postBody         
        processData: false
        error: (err) ->
          console.log err
        success: (response) ->
          ids = ( loc.substring(17, (loc.length - 1 )) for loc in response )
          $('#page-content').empty().append root.app.responseJade.content { newResources: ids }
      $.ajax opts
      
  root.app = new HarvestApplication()
