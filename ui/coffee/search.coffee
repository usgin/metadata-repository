root = exports ? this

$(document).ready ->
  
  class SearchApplication extends Backbone.View
    jade: new root.Jade '/static/templates/search-application.jade'
    
    paginatorJade: new root.Jade '/static/templates/paginator.jade'
    
    limit: 10
    
    el: $ '#page-content'
    
    results: new Resources()
    
    initialize: (options) ->
      @render()      
      return
    
    render: ->      
      @$el.append @jade.content { term: root.term }             
      return @
    
    renderResults: (results) ->
      # Deal with result count
      $('#result-count').html "Your search returned #{results.total_rows} results"
      
      # Add the results to the page
      root.app.results.reset(new Resource(result) for result in results.results)
      $('#results').empty()
      root.app.results.forEach (resource) ->
        resultView = new root.SearchResultView { model: resource }
        $('#results').append resultView.render().el
      
      # Render the paginator
      root.app.renderPaginator results
      
    renderPaginator: (results) ->
      return if results.total_rows < root.app.limit
      context =
        pageCount: Math.ceil results.total_rows / root.app.limit
        currentPage: ( results.skip / root.app.limit ) + 1
      ele = $ '#page-switcher'
      ele.empty()
      ele.append root.app.paginatorJade.content context
        
    events:
      'click #search-button': 'searchButton'
      'keyup #search-terms': 'keycheck'
      'click .pager-item': 'pagination'
      
    doSearch: (skip=0) ->
      postBody =
        searchTerms: escape $('#search-terms').val()
        limit: root.app.limit
        skip: skip
      options = 
        type: 'POST'
        contentType: 'application/json'
        url: '/metadata/search/'
        data: JSON.stringify postBody         
        processData: false
        error: (err) ->
          console.log err
        success: root.app.renderResults
      $.ajax options
    
    searchButton: (event) ->
      @doSearch()
      
    keycheck: (event) ->
      @doSearch() if event.keyCode is 13
      
    pagination: (event) ->
      buttonId = event.target.id.split('-')[1]
      isNumber = (n) ->
        return !isNaN(parseFloat n) && isFinite n    
      if isNumber buttonId
        skip = (parseInt(buttonId) - 1 ) * root.app.limit
        root.app.doSearch skip
      else
        current = $('.pager-current').attr('id').split('-')[1]
        switch buttonId
          when 'first' then root.app.doSearch 0     
          when 'pre'
            skip = ( current - 2 ) * root.app.limit
            root.app.doSearch skip
          when 'nxt'
            skip = current * root.app.limit
            root.app.doSearch skip
          when 'last' 
            skip = ( parseInt($('#pager-last').attr('last')) - 1 ) * root.app.limit
            root.app.doSearch skip
          
  root.app = new SearchApplication()
  root.app.doSearch() if root.term isnt null and root.term isnt ''
