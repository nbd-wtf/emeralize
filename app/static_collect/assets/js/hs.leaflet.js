/*
* Leaflet wrapper
* @version: 2.0.0 (Sat, 22 May 2021)
* @requires: Leafletjs v1.6.0
* @author: HtmlStream
* @event-namespace: .HSCore.components.HSLeaflet
* @license: Htmlstream Libraries (https://htmlstream.com/licenses)
* Copyright 2021 Htmlstream
*/

function isObject(item) {
  return (item && typeof item === 'object' && !Array.isArray(item));
}

function mergeDeep(target, ...sources) {
  if (!sources.length) return target;
  const source = sources.shift();

  if (isObject(target) && isObject(source)) {
    for (const key in source) {
      if (isObject(source[key])) {
        if (!target[key]) Object.assign(target, { [key]: {} });
        mergeDeep(target[key], source[key]);
      } else {
        Object.assign(target, { [key]: source[key] });
      }
    }
  }

  return mergeDeep(target, ...sources);
}

HSCore.components.HSLeaflet = {
  init: function (el, options) {
    this.$el = typeof el === "string" ? document.querySelector(el) : el
    if (!this.$el) return

    this.defaults = {
      map: {
        coords: [51.505, -0.09],
        zoom: 13
      },
      layer: {
        token: 'https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw',
        id: 'mapbox/streets-v11',
        maxZoom: 18
      },
      marker: null
    }
    var dataSettings = this.$el.hasAttribute('data-hs-leaflet-options') ? JSON.parse(this.$el.getAttribute('data-hs-leaflet-options')) : {}

    this.settings = mergeDeep(this.defaults, {...options, ...dataSettings})

    /* Start : Init */

    var newLeaflet = L.map(this.$el, this.settings.map)

    /* End : Init */

    /* Start : custom functionality implementation */

    // View
    newLeaflet.setView(this.settings.map.coords, this.settings.map.zoom)

    // Layer
    L.tileLayer(this.settings.layer.token, this.settings.layer).addTo(newLeaflet)

    // Marker
    if (this.settings.marker) {
      for (var i = 0; i < this.settings.marker.length; i++) {
        this.settings.marker[i].icon = L.icon(this.settings.marker[i].icon);

        let marker = L.marker(this.settings.marker[i].coords, this.settings.marker[i]).addTo(newLeaflet)

        if (this.settings.marker[i].popup) {
          marker.bindPopup(this.settings.marker[i].popup.text)
        }
      }
    }

    /* End : custom functionality implementation */

    return newLeaflet
  }
};
