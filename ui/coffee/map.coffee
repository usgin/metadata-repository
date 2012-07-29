root = exports ? this

# Convert mercator bounds to geographic bounds
mercToGeo = (mercBounds) ->
  geoPoint = (x, y) ->
    pt = new OpenLayers.Geometry.Point x, y
    return OpenLayers.Layer.SphericalMercator.inverseMercator pt.x, pt.y
  lbGeo = geoPoint mercBounds.left, mercBounds.bottom
  rtGeo = geoPoint mercBounds.right, mercBounds.top
  return new OpenLayers.Bounds lbGeo.lon, lbGeo.lat, rtGeo.lon, rtGeo.lat

# Convert geographic bounds to mercator bounds
geoToMerc = (geoBounds) ->
  mercPoint = (x, y) ->
    pt = new OpenLayers.Geometry.Point x, y
    return OpenLayers.Layer.SphericalMercator.forwardMercator(pt.x, pt.y)
  lb = mercPoint geoBounds.left, geoBounds.bottom
  rt = mercPoint geoBounds.right, geoBounds.top
  return new OpenLayers.Bounds lb.lon, lb.lat, rt.lon, rt.lat
  
$(document).ready ->
  # Make a map
  map = new OpenLayers.Map 'map', {
    controls: [
      new OpenLayers.Control.Navigation()
      new OpenLayers.Control.ZoomPanel()
    ]
  }  

  # Add the Google Physical Basemap
  physical = new OpenLayers.Layer.Google 'Google Physical', { type: google.maps.MapTypeId.TERRAIN }, { wrapDateLine: true, isBaseLayer: true }
  map.addLayer(physical)

  # Add a Vector Layer to contain the record's extent
  vector = new OpenLayers.Layer.Vector()
  map.addLayer(vector)
  
  if geoExtent?
    # geoExtent is passed in through resource.jade template rendering
    #   Convert it to Mercator  
    mercBounds = geoToMerc geoExtent
    
    # Add the vector feature and zoom to it
    poly = mercBounds.toGeometry()
    vector.addFeatures [ new OpenLayers.Feature.Vector poly ]
    map.zoomToExtent mercBounds
  
  # Add toolbars if this is an editable map page
  editToolbars map, vector if root.update?

editToolbars = (map, vectorLayer) ->
  # Build the Draw Box control
  controlDrawBox = new OpenLayers.Control {
    draw: ->
      @box = new OpenLayers.Handler.Box @, { start: @start, done: @done }
      @box.activate()
      return
    start: ->
      vectorLayer.removeAllFeatures()
      return
    done: (bounds) ->
      # Convert pixel values to map coordinates
      lt = map.getLonLatFromPixel new OpenLayers.Pixel bounds.left, bounds.top
      rb = map.getLonLatFromPixel new OpenLayers.Pixel bounds.right, bounds.bottom
      
      # Get the bounding box
      bbox = new OpenLayers.Bounds lt.lon, rb.lat, rb.lon, lt.lat
      
      # Convert to geographic coords
      geoBbox = mercToGeo bbox
      
      # Check for geometry that crosses the date line
      if geoBbox.left > geoBbox.right
        geoBbox.right = 360 + geoBbox.right
        
        # Update the Mercator bounding box
        bbox = geoToMerc geoBbox
        
      # Show the bounding box on the map  
      mapBbox = new OpenLayers.Feature.Vector bbox.toGeometry()
      vectorLayer.addFeatures [ mapBbox ]
      
      # Set the GeographicExtent part of the record form
      recordExtent =
        NorthBound: geoBbox.top
        SouthBound: geoBbox.bottom
        EastBound: geoBbox.right
        WestBound: geoBbox.left
      root.app.geographicExtentView.model.set recordExtent
      root.app.geographicExtentView.render()
      
      # Disable the "Add Box" button
      $('#add-box').click()
      return
  }

  # Build the Modify control
  controlModify = new OpenLayers.Control.ModifyFeature vectorLayer, {
    mode: OpenLayers.Control.ModifyFeature.RESIZE | OpenLayers.Control.ModifyFeature.DRAG
  }
  
  # jQuery pointers
  addBoxEle = $('#add-box')
  modBoxEle = $('#modify-box')
  
  # Setup the UI buttons through jQuery
  addBoxEle.toggle(
    ->
      modBoxEle.click() if modBoxEle.hasClass 'ui-state-press'
      map.addControl controlDrawBox
      addBoxEle.addClass 'ui-state-press'
      return
    , 
    ->
      map.removeControl controlDrawBox
      addBoxEle.removeClass 'ui-state-press'
      return
  )
  
  modBoxEle.toggle(
    ->
      addBoxEle.click() if addBoxEle.hasClass 'ui-state-press'
      map.addControl controlModify
      controlModify.activate()
      modBoxEle.addClass 'ui-state-press'
      return
    ,
    ->
      controlModify.deactivate()
      map.removeControl controlModify
      modBoxEle.removeClass 'ui-state-press'
      return        
  )
  
  # Register function to fire when features are modified
  vectorLayer.events.register 'afterfeaturemodified', @, (evt) ->
    bounds = mercToGeo evt.feature.geometry.bounds
    wrappedCoord = (coord) ->
      return 360 + coord if coord < -180
      return coord - 360 if coord > 180
      return coord
    bounds.left = wrappedCoord bounds.left
    bounds.right = wrappedCoord bounds.right
    
    # Set the GeographicExtent part of the record form
    recordExtent =
      NorthBound: bounds.top
      SouthBound: bounds.bottom
      EastBound: bounds.right
      WestBound: bounds.left
    root.app.geographicExtentView.model.set recordExtent
    root.app.geographicExtentView.render()
    return

  return