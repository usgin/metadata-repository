root = exports ? this

class root.CollectionsView extends Backbone.View
  jade: new root.Jade '/static/templates/edit-collection.jade'
  
  confirmation: new root.Jade '/static/templates/confirmation-dialog.jade'
  
  newCollection: new root.Jade '/static/templates/new-collection-dialog.jade'
  
  tagName: 'ul'
  
  id: 'collections-current-list'
  
  className: 'menu'
  
  parentId: '#collections-content'
  
  initialize: (options) ->
  
  render: ->
    @$el.empty()
    @$el.append @jade.content col.toJSON() for col in @model.models
    @$el.append '<li id="add-to-collection" class="link-ish">Add to a new Collection</li>'
    $(@parentId).append @$el
    return @
    
  events:
    'click #add-to-collection': 'addToCollection',
    'click .deleteCollection': 'deleteCollection'
    
  addToCollection: ->    
    # Show the dialog to select a new collection
    $('#page-content').append @newCollection.content {}
    $('#new-collection-selector').autocomplete {
      source: ({ id: col.id, value: col.title } for col in root.allCollections)
      select: (evt, ui) ->
        $('#new-selected-collection').val ui.item.id
        $(this).val ui.item.value
        return false
    }
    $('#add-collection-dialog').dialog {
      resizable: false
      width: 500
      modal: true
      buttons:
        "Add to selected collection": ->          
          # Get the new collection Id
          id = $('#new-selected-collection').val()
          
          # Function to update the UI
          updateUi = ->
            col = new ResourceCollection { id: id, title: $('#new-collection-selector').val(), can_edit: true }
            root.app.collectionsView.model.add col
            root.app.collectionsView.render()                      
          
          if update
            # Run the command to update the record with the new collection
            cols = root.app.record.get 'Collections'
            cols.push id
            root.app.record.set 'Collections', cols
            opts =
              type: 'PUT'
              url: "/metadata/record/#{root.app.record.id}/"
              processDate: false
              contentType: 'application/json'
              data: JSON.stringify root.app.record.toJSON()
              error: (err) ->
                console.log err
              success: (response) ->
                updateUi()
                $('#add-collection-dialog').dialog 'close'
                $('#add-collection-dialog').remove()
            $.ajax opts
          else
            updateUi()
            $(this).dialog 'close'
            $(this).remove()          
        Cancel: ->
          $(this).dialog 'close'
          $(this).remove()
          
    }

  deleteCollection: (evt) ->
    # Get the collection Id
    id = evt.currentTarget.id.split('-')[0]
    
    # Confirm that they want to remove this record from the specified collection
    $('#page-content').append @confirmation.content { title: 'Remove from collection?', message: "Remove this record from '#{$(evt.currentTarget).parent().next().text()}'?" }
    
    # Function to update the UI
    updateUi = ->
      col = root.app.collectionsView.model.get id
      root.app.collectionsView.model.remove col
      root.app.collectionsView.render()
        
    $('#dialog-confirm').dialog {
      resizable: false
      height: 160
      modal: true
      buttons : {
        "Remove": ->
          if update
            # Run the command to remove the record 
            cols = root.app.record.get 'Collections'
            root.app.record.set 'Collections', ( col for col in cols when col isnt id )
            opts =
              type: 'PUT'
              url: "/metadata/record/#{root.app.record.id}/"
              processData: false
              contentType: 'application/json'
              data: JSON.stringify root.app.record.toJSON()
              error: (err) ->
                console.log err
              success: (response) ->
                updateUi()                        
            $.ajax opts
          else
            updateUi()
          $(this).dialog 'close'
          $(this).remove()
        Cancel: ->
          $(this).dialog 'close'
          $(this).remove()
      }
    }
       
class root.FilesView extends Backbone.View
  fileJade: new root.Jade '/static/templates/edit-file.jade'
  
  confirmationJade: new root.Jade '/static/templates/confirmation-dialog.jade'
  
  newFileJade: new root.Jade '/static/templates/file-upload-dialog.jade'
  
  tagName: 'ul'
  
  className: 'menu'
  
  id: 'file-attachments-list'
  
  parentId: '#file-attachment-content'   

  render: ->
    @$el.empty()
    @$el.append @fileJade.content file.toJSON() for file in @model.models
    if update
      @$el.append '<li id="add-new-file" class="link-ish">Attach a new file</li>'
    else
      @$el.append '<li id="no-files-yet">Please save your record before attaching files</li>'
    $(@parentId).append @$el
    return @

  events:
    'click #add-new-file': 'addFile'
    'click .deleteFile': 'deleteFile'
    
  addFile: ->
    $('#page-content').append @newFileJade.content { id: root.app.record.id }
    $('#new-file-dialog').dialog {
      resizable: false
      width: 400      
      modal: true
      buttons:
        "Upload File": ->          
          $('#new-file-form').ajaxForm()
          $('#new-file-form').ajaxSubmit {
            success: (data, status, xhr) ->
              # Update the UI
              loc = xhr.getResponseHeader('Location')
              f = new FileAttachment { filename: loc.split('/').pop(), location: loc }
              root.app.filesView.model.add f
              root.app.filesView.render()
              $('#new-file-dialog').dialog 'close'
              $('#new-file-dialog').remove()
          }                               
        Cancel: ->
          $(this).dialog 'close'
          $(this).remove()
    }

  deleteFile: (evt) ->
    id = evt.currentTarget.id.split('-')[0]
    
    # Confirm that they want to remove this record from the specified collection
    $('#page-content').append @confirmationJade.content { title: 'Delete File?', message: "Delete #{id}?" }
    $('#dialog-confirm').dialog {
      resizable: false
      height: 160
      modal: true
      buttons:
        "Remove": ->
          opts = 
            type: 'DELETE'
            url: "/metadata/record/#{root.app.record.id}/file/#{id}"
            error: (err) ->
              console.log err
            success: (data, status, xhr) ->
              # Update the UI
              f = root.app.filesView.model.get id
              root.app.filesView.model.remove f
              root.app.filesView.render() 
          $.ajax opts
          $(this).dialog 'close'
          $(this).remove()
        Cancel: ->
          $(this).dialog 'close'
          $(this).remove()
    }

# Views representing collections: Authors, Distributors, Links  
class root.AuthorsView extends Backbone.View
  id: 'authors'
  
  className: 'required array-container'
  
  jade: new root.Jade '/static/templates/edit-authors.jade'
  
  parentId: '#resource-container'
  
  render: ->
    @$el.empty()
    @$el.append @jade.content {}
    @$el.insertAfter $('#geographic-extent')
    (new root.AuthorView { model: model }).render() for model in @model.models
    return @

  events:
    'click legend:first > span': 'collapse'
    'click .add-button': 'newAuthor'
    'click .add-contact-button': 'addContact'
    
  collapse: (evt) ->
    collapseFieldsets evt.target
    
  newAuthor: ->
    newAuthor = new root.Contact {}
    @model.add newAuthor
    authorView = new root.AuthorView { model: newAuthor }    
    authorView.render()
    
  addContact: ->
    dialog = $('#select-contact-dialog')
    dialog.unbind()
    dialog.bind 'dialogclose', (evt, ui) ->
      contact = root.app.contacts[$('#contact-selector').val()]
      newAuthor = new root.Contact contact
      root.app.authorsView.model.add newAuthor
      authorView = new root.AuthorView { model: newAuthor }    
      authorView.render()
    dialog.dialog 'open'
    
class root.DistributorsView extends Backbone.View
  id: 'distributors'
  
  className: 'required array-container'
  
  jade: new root.Jade '/static/templates/edit-distributors.jade'
  
  parentId: '#resource-container'
  
  render: ->
    @$el.empty()
    @$el.append @jade.content {}
    @$el.insertAfter $ '#authors'
    (new root.DistributorView { model: model }).render() for model in @model.models
    root.app.autocompleteDistributors()
    return @
    
  events:
    'click legend:first > span': 'collapse'
    'click .add-button': 'newDistributor'
    'click .add-contact-button': 'addContact'
    
  collapse: (evt) ->
    collapseFieldsets evt.target

  newDistributor: ->
    newDist = new root.Contact {}
    @model.add newDist
    distView = new root.DistributorView { model: newDist }    
    distView.render()
    
  addContact: ->
    dialog = $('#select-contact-dialog')
    dialog.unbind()
    dialog.bind 'dialogclose', (evt, ui) ->
      contact = root.app.contacts[$('#contact-selector').val()]
      newDist = new root.Contact contact
      root.app.distributorsView.model.add newDist
      distView = new root.DistributorView { model: newDist }    
      distView.render()
    dialog.dialog 'open'
    
class root.LinksView extends Backbone.View
  id: 'links'
  
  className: 'required array-container'
  
  jade: new root.Jade '/static/templates/edit-links.jade'
  
  parentId: '#resource-container'
  
  render: ->
    @$el.empty()
    @$el.append @jade.content {}
    #$(@parentId).append @$el
    @$el.insertAfter $ '#distributors'
    (new root.LinkView { model: model }).render() for model in @model.models
    root.app.autocompleteDistributors()
    return @
    
  events:
    'click legend:first > span': 'collapse'
    'click .add-file-button': 'addLink'
    'click .add-service-button': 'addServiceLink'
    
  collapse: (evt) ->
    collapseFieldsets evt.target

  addLink: ->
    link = new root.Link { schemaName: 'link' }
    link.schema = root.app.schemas.link
    root.app.linksView.model.add link
    root.app.linksView.render()
    
  addServiceLink: ->
    link = new root.Link { schemaName: 'serviceLink' }
    link.schema = root.app.schemas.serviceLink
    root.app.linksView.model.add link
    root.app.linksView.render()
    
# Additional Styling Functions
resizeInputs = (index, ele) ->
  ele = $(ele)
  eleWidth = ele.innerWidth()
  border = if ele.hasClass 'required' then 3 else 5
  spanWidth = if ele.children('span').length > 0 then ele.children('span').width() - border else 0
  additional = if ele.children('.remove-button').length > 0 then 5 else 21
  ele.children('input, select').width eleWidth - spanWidth - additional
  return
  
collapseFieldsets = (target) ->
  ele = $ target
  ele.parent().toggleClass 'collapsed'
  isCollapsed = ele.parent().hasClass 'collapsed'
  fieldset = ele.parent().parent()
  if isCollapsed then fieldset.css('height', 45) else fieldset.css('height', 'auto')
  fieldset.children().not('legend').each (index, ele) ->
    if isCollapsed then $(@).addClass 'hidden' else $(@).removeClass 'hidden'    

class root.BasicMetadataView extends Backbone.View
  id: 'basic-metadata'
  
  jade: new root.Jade '/static/templates/edit-basic-metadata.jade'
  
  parentId: '#resource-container'
  
  render: ->
    @$el.empty()
    @$el.append @jade.content @model.toJSON()
    $(@parentId).prepend @$el
    @$el.find(".key-value").each resizeInputs
    @$el.find('input[attr="PublicationDate"]').datepicker {
      dateFormat: "yy-mm-ddT00:00:00"
      changeMonth: true
      changeYear: true
    } 
    return @
    
  events:
    'click legend > span': 'collapse'
    'change input, textarea': 'changeAttribute'
    'click .add-button': 'newKeyword'
    'click .remove-button': 'removeKeyword'
    
  collapse: (evt) ->
    collapseFieldsets evt.target

  changeAttribute: (evt) ->
    ele = $ evt.target
    attr = ele.attr 'attr'
    value = if attr is 'Published' then ele.is ':checked' else ele.val()
    if attr is 'Keyword'
      attr = 'Keywords'
      value = ( $(input).val() for input in $('#keywords-list').find('input') )      
    @model.set attr, value
    return
    
  newKeyword: ->
    keys = @model.get 'Keywords'
    keys.splice 0, 0, ''
    @model.set 'Keywords', keys
    @render()
  removeKeyword: (evt) ->
    rem = $(evt.target).siblings('input').val()
    keys = @model.get 'Keywords'
    @model.set 'Keywords', ( key for key in keys when key isnt rem )
    @render()
  

class root.ContactView extends Backbone.View
  tagName: 'li'
  
  className: 'object-container'
  
  contactJade: new root.Jade '/static/templates/edit-contact.jade'
  contactInfoJade: new root.Jade '/static/templates/edit-contact-information.jade'
  addressJade: new root.Jade '/static/templates/edit-address.jade'
  confirmationJade: new root.Jade '/static/templates/confirmation-dialog.jade'
  
  render: ->
    @$el.append @contactJade.content @model.toJSON()
    @$el.find('.contact-information').append @contactInfoJade.content @model.contactInformation.toJSON()
    @$el.find('.address').append @addressJade.content @model.contactInformation.address.toJSON()
    
    $(@parentId).prepend @$el    
    @$el.find(".key-value").each resizeInputs
    @$el.find('legend:first > span').addClass 'distributor-title' if @parentId is '#distributors-list'
    return @
    
  events:
    'click legend > span': 'collapse'
    'click .remove-array-item-button': 'removeContact'
    'change input': 'changeAttribute'
    
  collapse: (evt) ->
    collapseFieldsets evt.target
  
  removeContact: (evt) ->
    # Confirm that they want to remove this record from the specified collection
    self = @
    $('#page-content').append @confirmationJade.content { title: 'Remove Contact?', message: "Are you sure you want to remove this contact?" }
    $('#dialog-confirm').dialog {
      resizable: false
      height: 160
      modal: true
      buttons:
        "Remove": ->
          contactsView = if self.parentId is '#authors-list' then root.app.authorsView else root.app.distributorsView
          contactsView.model.remove self.model
          contactsView.render()
          $(this).dialog 'close'
          $(this).remove()
        Cancel: ->
          $(this).dialog 'close'
          $(this).remove()
    }    

  changeAttribute: (evt) ->
    ele = $ evt.target
    attr = ele.attr 'attr'
    value = ele.val()
    model = @model
    if attr in [ 'Phone', 'email' ]
      model = @model.contactInformation
    if attr in [ 'Street', 'City', 'State', 'Zip' ]
      model = @model.contactInformation.address       
    model.set attr, value
    @adjustContactTitle() if attr in [ 'Name', 'OrganizationName' ]
    root.app.autocompleteDistributors() if @parentId is '#distributors-list'
    return
    
  adjustContactTitle: ->
    name = @model.get 'Name'
    orgName = @model.get 'OrganizationName'
    val = if name in [ '', 'No Name Was Given' ] and orgName? then orgName else name
    if @parentId is '#distributors-list'
      $(linkDist).val(val) for linkDist in $ '.distributors' when $(linkDist).val() is @$el.find('legend:first > span').html()
    @$el.find('legend:first > span').html(val)
            
class root.AuthorView extends root.ContactView
  parentId: '#authors-list'
    
class root.DistributorView extends root.ContactView
  parentId: '#distributors-list'
    
class root.GeographicExtentView extends Backbone.View
  id: 'geographic-extent'
  
  className: 'required object-container'
  
  parentId: '#resource-container'
  
  jade: new root.Jade '/static/templates/edit-geographic-extent.jade'
  
  render: ->
    @$el.empty()
    @$el.append @jade.content @model.toJSON()
    @$el.insertAfter $('#basic-metadata')
    @$el.find(".key-value").each resizeInputs
    return @
    
  events:
    'click legend > span': 'collapse'
    'change input': 'changeAttribute'
    
  collapse: (evt) ->
    collapseFieldsets evt.target
    
  changeAttribute: (evt) ->
    ele = $ evt.target
    attr = ele.attr 'attr'  
    @model.set attr, parseInt ele.val()
    
class root.LinkView extends Backbone.View
  parentId: '#links-list'
  
  tagName: 'li'
  
  className: 'object-container'
  
  jade: new root.Jade '/static/templates/edit-link.jade'
  confirmationJade: new root.Jade '/static/templates/confirmation-dialog.jade'
  
  render: ->
    @$el.append @jade.content @model.toJSON()
    $(@parentId).prepend @$el
    @$el.find(".key-value").each resizeInputs
    return @
  
  events:
    'click legend > span': 'collapse'
    'click .remove-array-item-button': 'removeLink'
    'change input, select': 'changeAttribute'
    
  collapse: (evt) ->
    collapseFieldsets evt.target
    
  removeLink: (evt) ->
    # Confirm that they want to remove this record from the specified collection
    self = @
    $('#page-content').append @confirmationJade.content { title: 'Remove Link?', message: "Are you sure you want to remove this link?" }
    $('#dialog-confirm').dialog {
      resizable: false
      height: 160
      modal: true
      buttons:
        "Remove": ->          
          root.app.linksView.model.remove self.model
          root.app.linksView.render()
          $(this).dialog 'close'
          $(this).remove()
        Cancel: ->
          $(this).dialog 'close'
          $(this).remove()
    }    
  
  changeAttribute: (evt) ->
    ele = $ evt.target
    attr = ele.attr 'attr'  
    @model.set attr, ele.val()
    @adjustLinkTitle() if attr in [ 'Name', 'URL', 'ServiceType' ]      
  
  adjustLinkTitle: ->
    st = @model.get 'ServiceType'
    url = @model.get 'URL'
    name = @model.get 'Name'
    val = url
    val = st if st? and st isnt ''
    val = name if name? and name isnt ''
    @$el.find('legend span').html val
      



