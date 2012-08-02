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
      
      # Event listeners
      @on 'schemasLoaded', ->
        @parseRecord()
        
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
              $(this).dialog 'close'
        }
        
      # Push site info to the bottom
      $("#site-info-block").insertAfter "#map-block"
      
      # Setup Save and Delete buttons
      $('.save-button, .delete-button').button()
      $('.save-button').click @saveRecord
      $('.delete-button').click @deleteRecord
      
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
        l.schema = if link.ServiceType? then @schemas.serviceLink else @schemas.link
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
      
  root.app = new App()
