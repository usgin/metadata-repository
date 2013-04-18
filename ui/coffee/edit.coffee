root = exports ? this

$(document).ready ->
  class App extends Backbone.View
    record: new Resource root.inputRecord or {}
    collections: new ResourceCollections()    
    schemas: {}
    contactJade: new root.Jade '/static/templates/select-contact-dialog.jade'
    confirmationJade: new root.Jade '/static/templates/confirmation-dialog.jade'
    
    initialize: (options) ->
      # Setup the collections in the sidebar
      cols = ( new ResourceCollection col for col in inputCollections )
      @collections.add cols
      @collectionsView = new CollectionsView({ model: @collections })
      @collectionsView.render()
      
      # Setup file attachments sidebar
      recId = null
      recId = root.inputRecord.id if root.inputRecord?
        
      @files = new FileAttachments(null, { recordId: recId })
      @files.on 'loaded', ->
        root.app.filesView = new FilesView({ model: root.app.files })
        root.app.filesView.render()
      
      # Load schemas
      getSchema = (self, schemaName, resolve=false) ->
        resolve = true if schemaName in [ 'serviceLink', 'contact' ]
        opts = 
          url: "/metadata/schema/#{schemaName}/"
          type: 'GET'
          data:
            resolve: resolve
          error: (err) ->
            console.log err
          success: (data, status, xhr) ->
            self.schemas[schemaName] = data
            if ( key for key, value of self.schemas ).length is schema_list.length
              self.trigger 'schemasLoaded'
        $.ajax opts
      schema_list = [ 'link', 'serviceLink', 'contact', 'contactInformation', 'address', 'geographicExtent', 'metadata' ]           
      getSchema @, schemaName for schemaName in schema_list      
      
      # Load Contacts
      opts =
        url: '/registry/contacts/'
        error: (err) ->
          console.log err
        success: (data, status, xhr) ->
          root.app.contacts = data
          root.app.trigger 'contactsLoaded'
      $.ajax opts
      
      # Parse the record once schemas are loaded
      @on 'schemasLoaded', ->
        @parseRecord()
      
      # Initialize the contacts dialog once contacts are loaded
      @on 'contactsLoaded', ->
        $('#page-content').append @contactJade.content {}
        $('#contact-selector').autocomplete {
          source: (key for key, value of @contacts)
        }
        $('#select-contact-dialog').dialog {
          autoOpen: false
          resizable: false
          width: 600
          modal: true
          buttons:
            'Add selected contact': ->
              $(this).dialog 'close'
            Cancel: ->
              $('#contact-selector').val ''
              $(this).dialog 'close'
        }
        
      # Push site info to the bottom
      $("#site-info-block").insertAfter "#map-block"
      
      # Setup Save and Delete buttons
      $('.save-button, .delete-button, .validate-button').button()
      $('.save-button').click @saveRecord
      $('.delete-button').click @deleteRecord
      $('.validate-button').click @validateRecord
      
    parseRecord: ->
      # Parse the record into its components.      
      # Basic metadata information
      @record.basicMetadata = new root.BasicMetadata {
        Title: @record.get 'Title'
        Description: @record.get 'Description'
        Published: @record.get 'Published'
        PublicationDate: @record.get 'PublicationDate'
        ResourceId: @record.get 'ResourceId'
        Keywords: @record.get 'Keywords'
      }
      @record.basicMetadata.schema = @schemas.metadata
      
      # Authors
      @record.authors = new root.Contacts()
      for author in @record.get 'Authors'
        auth = new root.Contact author
        auth.schema = @schemas.contact
        @record.authors.add auth
      
      # Geographic extent
      @record.geographicExtent = new root.GeographicExtent @record.get 'GeographicExtent'
      @record.geographicExtent.schema = @schemas.geographicExtent
      
      # Distributors
      @record.distributors = new root.Contacts()
      for distributor in @record.get 'Distributors'
        dist = new root.Contact distributor
        dist.schema = @schemas.contact
        @record.distributors.add dist
      
      # Links
      @record.links = new root.Links()
      for link in @record.get 'Links'
        l = new root.Link link
        l.schema = if link.ServiceType? or link.schemaName is 'serviceLink' then @schemas.serviceLink else @schemas.link
        @record.links.add l
      
      #Render basic views.
      @basicMetadataView = new BasicMetadataView { model: @record.basicMetadata }
      @geographicExtentView = new GeographicExtentView { model: @record.geographicExtent }    
      @basicMetadataView.render()
      @geographicExtentView.render()
              
      # Render collection views.
      @authorsView = new AuthorsView { model: @record.authors }
      @distributorsView = new DistributorsView { model: @record.distributors }
      @linksView = new LinksView { model: @record.links }
      @authorsView.render()
      @distributorsView.render()
      @linksView.render()
    
    autocompleteDistributors: ->
      $('.distributors').autocomplete {
        source: ( $(dist).html() for dist in $ '.distributor-title' )
        select: (evt, ui) ->
          url = $(evt.target).parent().parent().find('[attr="URL"]').val()
          link = root.app.linksView.getLinkByUrl url
          link.set 'Distributor', ui.item.value
      }
         
    saveRecord: ->
      $('#page-content').append root.app.confirmationJade.content { title: 'Save Changes?', message: "Are you sure you want to save your changes?" }
      $('#dialog-confirm').dialog {
        resizable: false
        height: 160
        modal: true
        buttons:
          "Save": ->                 
            opts =
              type: if update then 'PUT' else 'POST'
              url: if update then "/metadata/record/#{root.app.record.id}/" else '/metadata/record/'
              contentType: 'application/json'
              parseData: false
              data: JSON.stringify root.app.writeOutRecord()
              error: (err) ->
                if err.status is 400 and err.responseText.match 'validation'
                  root.app.validateRecord()
                console.log err
              success: (data, status, xhr) ->
                if update
                  window.location.href = "/repository/resource/#{root.app.record.id}/"
                else
                  id = xhr.getResponseHeader('Location').match(/\/(.{32})\/$/)[1]
                  window.location.href = "/repository/resource/#{id}/"
            $.ajax opts
            $(this).dialog 'close'
            $(this).remove()
          Cancel: ->
            $(this).dialog 'close'
            $(this).remove()
      }
      
    deleteRecord: ->
      $('#page-content').append root.app.confirmationJade.content { title: 'Delete Resource?', message: "Are you sure you want to completely delete this resource?" }
      $('#dialog-confirm').dialog {
        resizable: false
        height: 160
        modal: true
        buttons:
          "Delete Resource": ->          
            opts =
              type: 'DELETE'
              url: "/metadata/record/#{root.app.record.id}/"
              error: (err) ->
                console.log err
              success: (data, status, xhr) ->
                window.location.href = '/repository/search/'
            $.ajax opts                
            $(this).dialog 'close'
            $(this).remove()
          Cancel: ->
            $(this).dialog 'close'
            $(this).remove()
      }
      
    writeOutRecord: ->
      recordJson = JSON.parse JSON.stringify @record
      basics = JSON.parse JSON.stringify @basicMetadataView.model
      geo = { GeographicExtent: JSON.parse JSON.stringify @geographicExtentView.model }
      authors = { Authors: (author.writeOut() for author in @authorsView.model.models) }
      distributors = { Distributors: (distributor.writeOut() for distributor in @distributorsView.model.models) }
      links = { Links: (JSON.parse JSON.stringify link for link in @linksView.model.models) }
      collections = { Collections: ((JSON.parse JSON.stringify collection).id for collection in @collectionsView.model.models) }
      return _.extend recordJson, basics, geo, authors, distributors, links, collections
    
    # This is very lame, since validation is being provided by the metadata-server already
    #   but this makes it easier to track which fields need to be adjusted since the 
    #   metadata-server does not return information about WHY validation failed.
    validateRecord: ->
      messages = []
      # Check that required content is filled in
      $('.required').each ->
        $(this).removeClass 'invalid'
        userInput = $(this).find('[attr]')[0]
        if userInput.tagName.toLowerCase() not in ['ul'] and $(userInput).val() in ['', null]
          $(this).addClass 'invalid'
          messages.push "A #{$(userInput).attr('attr')} is required"
      
      # Check that at least one Author and Distributor are listed
      $('#authors-list, #distributors-list, #keywords-list').each ->
        $(this).parent('fieldset').removeClass 'invalid'
        if $(this).children('li').length is 0
          $(this).parent('fieldset').addClass 'invalid'
          type = $(this).attr('id').split('-')[0]
          type = type.replace type[0], type[0].toUpperCase()
          type = type.substring 0, type.length - 1
          messages.push "At least one #{type} is required."
      
      # Check that contacts specify a name or org name
      $('[attr="OrganizationName"]').each ->
        orgLi = $(this).parent('li')
        nameLi = orgLi.prev('li')        
        orgLi.removeClass 'invalid'
        nameLi.removeClass 'invalid'
        orgName = $(this).val()
        name = nameLi.children('[attr="Name"]').val()
        if name is '' and orgName is ''
          orgLi.addClass 'invalid'
          nameLi.addClass 'invalid'
          messages.push "A contact must specify either a Name or an Organization Name"
      
      # Check that the Description has at least 50 characters
      $('#basic-metadata #resource-description textarea').each ->
        desc = $(this).val()
        descLi = $(this).parent('#resource-description')
        descLi.removeClass 'invalid'
        if desc.length < 50
          descLi.addClass 'invalid'
          messages.push "Descriptions must contain at least 50 characters"
          
      # Check that GeographicExtent numbers fall within acceptable bounds
      $('#geographic-extent-list input').each ->
        extentLi = $(this).parent 'li'
        extentLi.removeClass 'invalid'
        extentVal = $(this).val()
        switch $(this).attr 'attr'
          when 'NorthBound'
            if extentVal > 90 or extentVal < -90
              extentLi.addClass 'invalid'
              messages.push 'NorthBound must be between -90 and 90'
          when 'SouthBound'
            if extentVal > 90 or extentVal < -90
              extentLi.addClass 'invalid'
              messages.push 'SouthBound must be between -90 and 90'
          when 'EastBound'
            if extentVal > 180 or extentVal < -180
              extentLi.addClass 'invalid'
              messages.push 'EastBound must be between -90 and 90'
          when 'WestBound'
            if extentVal > 180 or extentVal < -180
              extentLi.addClass 'invalid'
              messages.push 'WestBound must be between -90 and 90'
          
      # List validation messages
      msgContainer = $('#validation-message-container')
      msgContainer.children().each ->
        $(this).remove()
          
      if messages.length is 0
        msgContainer.addClass 'hidden'       
      else
        msgContainer.removeClass 'hidden'
        _.forEach messages, (msg) ->
          msgContainer.append "<li class='validation-error'>#{msg}</li>"
      
  root.app = new App()
