
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


// Create subfunctions for polygon layer

function showInfo() {
    this.setStyle({
        'fillColor': '#689ae9'
    });
}

function removeInfoPolygon() {
    scoreObject.resetStyle(this);
    }

// Create polygon layer and use onEachFeature to show certain info for each feature

var scoreObject = L.geoJSON(scoreObj, {
    style: function() {
        return {
            color: 'blue'
        }
    },
    onEachFeature: function (feature, layer) {
        myUrl = `http://dmapps/en/fisheriescape/fisheryarea/${feature.properties.pk}/view/`
        layer.bindPopup(`Name: <a href = "${myUrl}">${feature.properties.name}</a></br>Grid ID: ${feature.properties.grid_id}</br>Site Score: ${feature.properties.hexagon}`);
        layer.on({
            mouseover: showInfo,
            mouseout: removeInfoPolygon
        });
        }
});

// Test
const test = JSON.parse(document.getElementById("test-data").textContent);

// Define colour gradient for scores
function getColor(d) {
    return d > 10 ? '#800026' :
           d > 7  ? '#BD0026' :
           d > 5  ? '#E31A1C' :
           d > 4  ? '#FC4E2A' :
           d > 3   ? '#FD8D3C' :
           d > 2   ? '#FEB24C' :
           d > 1   ? '#FED976' :
                      '#FFEDA0';
}

// Define polygon style
function gradientStyle(feature) {
    // console.log(feature)
    return {
        fillColor: getColor(feature.properties.site_score),
        weight: 2,
        opacity: 1,
        color: 'white',
        dashArray: '3',
        fillOpacity: 0.7
    };
}

// Highlight the hexagon on mouseover
function highlightFeature(e) {
    var layer = e.target;

    layer.setStyle({
        weight: 5,
        color: '#666',
        dashArray: '',
        fillOpacity: 0.7
    });

    if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
        layer.bringToFront();
    }
    info.update(layer.feature.properties);
}

// Reset Highlight on mouseout
function resetHighlight(e) {
   overlay.resetStyle(e.target);
   info.update();
}

// Use this to simplify onEachFeature into block

// function onEachFeature(feature, layer) {
//     layer.on({
//         mouseover: highlightFeature,
//         mouseout: resetHighlight,
//         // click: zoomToFeature
//     });
// }

// Testing, this function takes in the getJSON call below and gets geoJson formatted data and makes layer
function createOverlay(data, layerName, style) {
  overlay = L.geoJson(data, { // Make the layer from the JSON and grab the handle.
    onEachFeature: function(feature, layer) {
       layer.bindPopup(`Species: ${feature.properties.species}</br>Week: ${feature.properties.week}</br>Site Score: ${feature.properties.site_score}`);
       layer.on({
           mouseover: highlightFeature,
           mouseout: resetHighlight,
       })
    },
    style: gradientStyle,
    // filter: function(feature) {
    //    return feature.properties.week === 'Week 25';
    // }
  });
  overlay.addTo(map);
  control.addOverlay(overlay, layerName); // Add the layer to the Layer Control.
}

// this works but had to add leaflet-ajax to static - but not sure how to get filter
$.getJSON(`http://127.0.0.1:8000/api/fisheriescape/scores-feature/`, function(data){
    createOverlay(data, "Site Scores")
});

// Create the map starting location and zoom level and tell it which layers to have on by default

var map = L.map('map3', {
    // center: [48.46, -61.95],
    // zoom: 6,
    layers: [streets, scoreObject] //this says what to have on by default
});

// Add hover info control box with info

var info = L.control({position: 'bottomleft'});

info.onAdd = function (map) {
    this._div = L.DomUtil.create('div', 'info'); // create a div with a class "info"
    this.update();
    return this._div;
};

// method that we will use to update the control based on feature properties passed
info.update = function (props) {
    this._div.innerHTML = '<h4>Fisheriescape Scores</h4>' +  (props ?
        '<b>' + props.species + '</b><br /> Site Score:' + props.site_score + '</b><br />' + props.week
        : 'Hover over a hexagon');
};

info.addTo(map);

// Custom Legend

var legend = L.control({position: 'bottomright'});

legend.onAdd = function (map) {

    var div = L.DomUtil.create('div', 'info legend'),
        grades = [1, 2, 3, 4, 5, 7, 10],
        labels = [];

    // loop through our density intervals and generate a label with a colored square for each interval
    for (var i = 0; i < grades.length; i++) {
        div.innerHTML +=
            '<i style="background:' + getColor(grades[i] + 1) + '"></i> ' +
            grades[i] + (grades[i + 1] ? '&ndash;' + grades[i + 1] + '<br>' : '+');
    }

    return div;
};

legend.addTo(map);


// Create basemaps variable and add basemaps desired to it as options

var baseMaps = {
    "Light": light,
    "Streets": streets,
};

var overlayMaps = {
    "Scores": scoreObject,
    // "test": overlay,

};


// Create the control layer box and add baseMaps and overlayMaps to it

var control = L.control.layers(baseMaps, overlayMaps).addTo(map);
map.fitBounds(scoreObject.getBounds(), {padding: [50, 50]});