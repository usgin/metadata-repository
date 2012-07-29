root = exports ? this

getEmptyInstance = (self, schemaName) ->
  opts =
    url: "/metadata/schema/#{schemaName}/"
    type: 'GET'
    async: false
    data:
      emptyInstance: true
    error: (err) ->
      console.log err
    success: (data, status, xhr) ->
      self.set data      
      
      # A couple of adjustments for metadata records...
      keys = (key for key, value of data)
      self.set 'Published', false if 'Published' in keys
      self.unset 'HarvestInformation' if 'HarvestInformation' in keys
  $.ajax opts
  
class root.Resource extends Backbone.Model
  initialize: (options) ->
    # Generate a blank contact from the schema if nothing was passed in
    if ( prop for prop, value of options ).length is 0
      getEmptyInstance @, 'metadata'
      
class root.Resources extends Backbone.Collection
  model: Resource
  
class root.ResourceCollection extends Backbone.Model
  toJSON: ->
    result =
      title: @.get('title')
      description: @.get('description')
      can_edit: @.get('can_edit')
      id: @id
      
  initialize: (options) ->
    @collections = new ResourceCollections()
    @resources = new Resources()
    if options.child_collections? and options.child_collections.length > 0      
      @collections.add new ResourceCollection(col) for col in options.child_collections
    if options.child_resources and options.child_resources.length > 0      
      @resources.add new Resource(rec) for rec in options.child_resources
    return
    
class root.ResourceCollections extends Backbone.Collection
  model: ResourceCollection 
  
# ------- The following models are used during the edit process ------- #
class root.FileAttachment extends Backbone.Model
  idAttribute: 'filename'
  
class root.FileAttachments extends Backbone.Collection
  model: root.FileAttachment
  
  initialize: (models, options) ->
    attachments = @
    if options.recordId?
      # Request the files for the specified record
      opts =
        type: 'GET'
        url: "/metadata/record/#{options.recordId}/file/"
        error: (err) ->
          console.log err
        success: (data, status, xhr) ->
          attachments.add new root.FileAttachment file for file in data
          attachments.trigger 'loaded'   
      $.ajax opts
    else
      setTimeout(->
        attachments.trigger 'loaded'
        , 1 )      

# These models all utilize 'getSchema' in order to find the schema that validates them
# Schema are loaded asynchronously, and the 'schemaLoaded' event is fired when the model is ready
class root.BasicMetadata extends Backbone.Model
  # This should include only basic metadata attributes:
  # Title, Description, Published, PublicationDate, ResourceId, Keywords
  initialize: (options) ->
  
class root.Contact extends Backbone.Model
  initialize: (options) ->
    # Generate a blank contact from the schema if nothing was passed in
    if ( prop for prop, value of options ).length is 0
      getEmptyInstance @, 'contact'
      
    # Push the Contact Information to a sub-model     
    @contactInformation = new root.ContactInformation @get 'ContactInformation'    
    @unset 'ContactInformation'
  
  writeOut: ->
    out = JSON.parse JSON.stringify @
    out.ContactInformation = JSON.parse JSON.stringify @contactInformation
    out.ContactInformation.Address = JSON.parse JSON.stringify @.contactInformation.address
    return out
    
class root.ContactInformation extends Backbone.Model
  initialize: (options) ->
    # Push Address information to a sub-model
    address = @get 'Address'
    if address?
      @address = new root.Address address      
      @unset 'Address'
      
class root.Address extends Backbone.Model
  initialize: (options) ->
    
class root.Contacts extends Backbone.Collection
  model: root.Contact
  
class root.GeographicExtent extends Backbone.Model
  initialize: (options) ->
  
class root.Link extends Backbone.Model
  initialize: (options) ->
    # Set the schemaName attribute
    schemaName = options.schemaName or 'link'
    schemaName = 'serviceLink' if options.ServiceType? 
    @set 'schemaName', schemaName
    
    # Generate a blank link from the schema if nothing was passed in
    if ( prop for prop, value of options when prop isnt 'schemaName' ).length is 0
      getEmptyInstance @, schemaName
    
  toJSON: ->
    result = 
      schemaName: @get 'schemaName'
    for prop, schema of @schema.properties
      result[prop] = @get(prop) or null
    return result
    
class root.Links extends Backbone.Collection
  model: root.Link
