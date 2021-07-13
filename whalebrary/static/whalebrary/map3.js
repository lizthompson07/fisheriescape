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
        layer.bindPopup(`Incident ID: ${feature.properties.id}<br>Incident Name: ${feature.properties.name}<br>Incident Type: ${feature.properties.type}</br>Species: ${feature.properties.species}</br>Date: ${feature.properties.date}`);
        }
});

// Create all incident layer and use onEachFeature to show certain info for each feature

var allPointObject = L.geoJSON(allPointObj, {

    onEachFeature: function (feature, layer) {
        myUrl = `http://dmapps/en/whalebrary/incident_detail/${feature.properties.pk}/view/`
        layer.bindPopup(`Incident ID: <a href = "${myUrl}">${feature.properties.id}</a><br>Incident Name: ${feature.properties.name}<br>Incident Type: ${feature.properties.type}</br>Species: ${feature.properties.species}</br>Date: ${feature.properties.date}`);
        }
});

// Create icon of different colour for resight (see https://awesomeopensource.com/project/pointhi/leaflet-color-markers)

var myIcon = new L.Icon({

  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

// Create all resight layer and use onEachFeature to show certain info for each feature

var resightObject = L.geoJSON(resightObj, {
     pointToLayer: function (feature, latlng) {
                    return L.marker(latlng, {icon: myIcon});
    },

    onEachFeature: function (feature, layer) {
       layer.bindPopup(`Resight #: ${feature.properties.pk}<br>Date: ${feature.properties.date}</br>Comments: ${feature.properties.comments}`);
       layer.bindTooltip(`${feature.properties.pk}`, {permanent: true, direction: 'top', offset: [1,10], className: 'pop-style'});
        }
});

// Create the map starting location and zoom level and tell it which layers to have on by default

var map = L.map('map3', {
    // center: [48.46, -61.95],
    // zoom: 6,
    layers: [streets, pointObject] //this says what to have on by default
});


// Get the fishing grid geojson information direct from geojson file - method 1

// $.getJSON($('link[rel="polygons"]').attr("href"), function(data) {
//     var fishingGrid = L.geoJson(data, {
//         onEachFeature: function (feature, layer) {
//             layer.bindPopup(feature.properties.GridName);
//         }
//     });
//
//     fishingGrid.addTo(map);
// });

// Get the fishing grid geojson information direct from geojson file using AJAX plugin - method 2

function popUp(feature, layer) {
    layer.bindPopup(feature.properties.Grid_Index);
  }

var fishingGrid = new L.GeoJSON.AJAX($('link[rel="polygons"]').attr("href"), {onEachFeature:popUp});


// Create basemaps variable and add basemaps desired to it as options

var baseMaps = {
    "Light": light,
    "Streets": streets,
};

var overlayMaps = {
    "incident": pointObject,
    "all incidents": allPointObject,
    "resights": resightObject,
    "fishing grids": fishingGrid,
};

// Create the control layer box and add baseMaps and overlayMaps to it

L.control.layers(baseMaps, overlayMaps).addTo(map);
map.fitBounds(pointObject.getBounds());
map.setZoom(6);

// add print buttons from https://github.com/rowanwins/leaflet-easyPrint

L.easyPrint({
	title: 'Save to .png',
	position: 'topleft',
	sizeModes: ['Current', 'A4Portrait', 'A4Landscape'],
    exportOnly: 'true'
}).addTo(map);

L.easyPrint({
	title: 'Print to pdf',
	position: 'topleft',
	sizeModes: ['Current', 'A4Portrait', 'A4Landscape']
}).addTo(map);
