// Create variable for different base maps

var light = L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
    maxZoom: 18,
    id: 'mapbox/light-v10',
    tileSize: 512,
    zoomOffset: -1,
    accessToken: mapboxApiKey});

var streets = L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
    maxZoom: 18,
    id: 'mapbox/streets-v11',
    tileSize: 512,
    zoomOffset: -1,
    accessToken: mapboxApiKey});

// Create specific incident layer and use onEachFeature to show certain info for each feature

var pointObject = L.geoJSON(pointObj, {

    onEachFeature: function (feature, layer) {
        layer.bindPopup(`Incident: ${feature.properties.name}`);
        }
});

// Create all incident layer and use onEachFeature to show certain info for each feature

var allPointObject = L.geoJSON(allPointObj, {

    onEachFeature: function (feature, layer) {
        layer.bindPopup(`Incident: ${feature.properties.name}`);
        }
});

// Create the map starting location and zoom level and tell it which layers to have on by default

var map = L.map('map3', {
    // center: [48.46, -61.95],
    // zoom: 6,
    layers: [streets, pointObject] //this says what to have on by default
});

// Create basemaps variable and add basemaps desired to it as options

var baseMaps = {
    "Light": light,
    "Streets": streets,
};

var overlayMaps = {
    "incident": pointObject,
    "all": allPointObject,

};

// Create the control layer box and add baseMaps and overlayMaps to it

L.control.layers(baseMaps, overlayMaps).addTo(map);
map.fitBounds(pointObject.getBounds());
map.setZoom(6);


// var markersLayer = L.markerClusterGroup()
// map.addLayer(markersLayer)
//
// function populateMap(data) {
// for (i in data) {
//   var name = data[i].name, //value searched
//     loc = data[i].loc, //position found
//     marker = new L.Marker(new L.LatLng(loc), {
//       title: name,
//
//     }) //se property searched
//   marker.bindPopup('<p>' + title + '</p>')
//   markersLayer.addLayer(marker)
// }
// }
//
// // use context variable instead of making AJAX call
// var map_incident = JSON.parse('{{ map_incident }}')
// var new_lat = map_incident[0].loc[0]
// var new_lon = map_incident[0].loc[1]
// map.setView([0, 0], 2)
// populateMap(map_incident)