(function() {
  var editToolbars, geoToMerc, mercToGeo, root;

  root = typeof exports !== "undefined" && exports !== null ? exports : this;

  mercToGeo = function(mercBounds) {
    var geoPoint, lbGeo, rtGeo;
    geoPoint = function(x, y) {
      var pt;
      pt = new OpenLayers.Geometry.Point(x, y);
      return OpenLayers.Layer.SphericalMercator.inverseMercator(pt.x, pt.y);
    };
    lbGeo = geoPoint(mercBounds.left, mercBounds.bottom);
    rtGeo = geoPoint(mercBounds.right, mercBounds.top);
    return new OpenLayers.Bounds(lbGeo.lon, lbGeo.lat, rtGeo.lon, rtGeo.lat);
  };

  geoToMerc = function(geoBounds) {
    var lb, mercPoint, rt;
    mercPoint = function(x, y) {
      var pt;
      pt = new OpenLayers.Geometry.Point(x, y);
      return OpenLayers.Layer.SphericalMercator.forwardMercator(pt.x, pt.y);
    };
    lb = mercPoint(geoBounds.left, geoBounds.bottom);
    rt = mercPoint(geoBounds.right, geoBounds.top);
    return new OpenLayers.Bounds(lb.lon, lb.lat, rt.lon, rt.lat);
  };

  $(document).ready(function() {
    var map, mercBounds, physical, poly, vector;
    map = new OpenLayers.Map('map', {
      controls: [new OpenLayers.Control.Navigation(), new OpenLayers.Control.ZoomPanel()]
    });
    physical = new OpenLayers.Layer.Google('Google Physical', {
      type: google.maps.MapTypeId.TERRAIN
    }, {
      wrapDateLine: true,
      isBaseLayer: true
    });
    map.addLayer(physical);
    vector = new OpenLayers.Layer.Vector();
    map.addLayer(vector);
    if (typeof geoExtent !== "undefined" && geoExtent !== null) {
      mercBounds = geoToMerc(geoExtent);
      poly = mercBounds.toGeometry();
      vector.addFeatures([new OpenLayers.Feature.Vector(poly)]);
      map.zoomToExtent(mercBounds);
    }
    if (root.update != null) return editToolbars(map, vector);
  });

  editToolbars = function(map, vectorLayer) {
    var addBoxEle, controlDrawBox, controlModify, modBoxEle;
    controlDrawBox = new OpenLayers.Control({
      draw: function() {
        this.box = new OpenLayers.Handler.Box(this, {
          start: this.start,
          done: this.done
        });
        this.box.activate();
      },
      start: function() {
        vectorLayer.removeAllFeatures();
      },
      done: function(bounds) {
        var bbox, geoBbox, lt, mapBbox, rb, recordExtent;
        lt = map.getLonLatFromPixel(new OpenLayers.Pixel(bounds.left, bounds.top));
        rb = map.getLonLatFromPixel(new OpenLayers.Pixel(bounds.right, bounds.bottom));
        bbox = new OpenLayers.Bounds(lt.lon, rb.lat, rb.lon, lt.lat);
        geoBbox = mercToGeo(bbox);
        if (geoBbox.left > geoBbox.right) {
          geoBbox.right = 360 + geoBbox.right;
          bbox = geoToMerc(geoBbox);
        }
        mapBbox = new OpenLayers.Feature.Vector(bbox.toGeometry());
        vectorLayer.addFeatures([mapBbox]);
        recordExtent = {
          NorthBound: geoBbox.top,
          SouthBound: geoBbox.bottom,
          EastBound: geoBbox.right,
          WestBound: geoBbox.left
        };
        root.app.geographicExtentView.model.set(recordExtent);
        root.app.geographicExtentView.render();
        $('#add-box').click();
      }
    });
    controlModify = new OpenLayers.Control.ModifyFeature(vectorLayer, {
      mode: OpenLayers.Control.ModifyFeature.RESIZE | OpenLayers.Control.ModifyFeature.DRAG
    });
    addBoxEle = $('#add-box');
    modBoxEle = $('#modify-box');
    addBoxEle.toggle(function() {
      if (modBoxEle.hasClass('ui-state-press')) modBoxEle.click();
      map.addControl(controlDrawBox);
      addBoxEle.addClass('ui-state-press');
    }, function() {
      map.removeControl(controlDrawBox);
      addBoxEle.removeClass('ui-state-press');
    });
    modBoxEle.toggle(function() {
      if (addBoxEle.hasClass('ui-state-press')) addBoxEle.click();
      map.addControl(controlModify);
      controlModify.activate();
      modBoxEle.addClass('ui-state-press');
    }, function() {
      controlModify.deactivate();
      map.removeControl(controlModify);
      modBoxEle.removeClass('ui-state-press');
    });
    vectorLayer.events.register('afterfeaturemodified', this, function(evt) {
      var bounds, recordExtent, wrappedCoord;
      bounds = mercToGeo(evt.feature.geometry.bounds);
      wrappedCoord = function(coord) {
        if (coord < -180) return 360 + coord;
        if (coord > 180) return coord - 360;
        return coord;
      };
      bounds.left = wrappedCoord(bounds.left);
      bounds.right = wrappedCoord(bounds.right);
      recordExtent = {
        NorthBound: bounds.top,
        SouthBound: bounds.bottom,
        EastBound: bounds.right,
        WestBound: bounds.left
      };
      root.app.geographicExtentView.model.set(recordExtent);
      root.app.geographicExtentView.render();
    });
  };

}).call(this);
