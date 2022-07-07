
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

// Create the map starting location and zoom level and tell it which layers to have on by default

var map = L.map('map4', {
    // center: [48.46, -61.95],
    // zoom: 6,
    layers: [streets, scoreObject] //this says what to have on by default
});

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