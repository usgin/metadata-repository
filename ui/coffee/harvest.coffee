root = exports ? this

$(document).ready ->
  
  class HarvestApplication extends Backbone.View
    jade: new root.Jade '/static/templates/harvest-application.jade'
    
    responseJade: new root.Jade '/static/templates/harvest-response.jade'
    
    el: $ '#harvest-button-container'
    
    initialize: (options) ->
      @render()
      
      # Setup the Collection Name autocomplete
      split = (val) ->
        return val.split /,\s*/
      
      extractLast = (term) ->
        return split(term).pop()
      
      getOpts = (elSelector, elVal) ->
        opts = 
          source: (req, res) ->
            res $.ui.autocomplete.filter root.collections, extractLast req.term
          focus: ->
            return false
          select: (event, ui) ->
            terms = split this.value
            terms.pop()
            terms.push ui.item.value
            terms.push ''
            
            ids = []
            for collection in root.collections
              for term in terms
                if collection.value == term then ids.push collection.id
            
            elSelector.val ids.join ", "
            $(this).val terms.join ", "
            return false
          change: (event, ui) ->
            terms = split this.value
  
            ids = []
            for collection in root.collections
              for term in terms
                if collection.value == term then ids.push collection.id
            elVal.val ids.join ", "
        return opts             
            
      $('#harvest-collection-selector').autocomplete getOpts $('#harvest-collection-selector'), $('#harvest-selected-collection')
      $('#upload-collection-selector').autocomplete getOpts $('#upload-collection-selector'), $('#upload-selected-collection')
      return 
      
    render: ->
      @$el.append @jade.content {}
      return @
      
    events:
      'click': 'doHarvest'
      
    doHarvest: ->
      collections = $('#harvest-selected-collection').val().split /,\s*/ 
      
      postBody =
        recordUrl: $('#input-url').val()
        inputFormat: $('input[name=harvestFormat]:checked').val()
        destinationCollections: collections
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
