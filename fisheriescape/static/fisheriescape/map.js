// Create some test points and group in a layer

var point1 = L.marker([48.76, -60.87]).bindPopup('Test 1'),
    point2 = L.marker([48.30, -63.68]).bindPopup('Test 2');

var tests = L.layerGroup([point1, point2]);

// Create variable for different base maps

var light = L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
    maxZoom: 18,
    id: 'mapbox/light-v10',
    tileSize: 512,
    zoomOffset: -1,
    accessToken: 'pk.eyJ1IjoibGl6dGhvbXBzb24wNyIsImEiOiJja2syeDlnNGswN3diMm5wY215NDAxZnY2In0.ZdCRCXWgROk6hSomUc6FSA'});

var streets = L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
    maxZoom: 18,
    id: 'mapbox/streets-v11',
    tileSize: 512,
    zoomOffset: -1,
    accessToken: 'pk.eyJ1IjoibGl6dGhvbXBzb24wNyIsImEiOiJja2syeDlnNGswN3diMm5wY215NDAxZnY2In0.ZdCRCXWgROk6hSomUc6FSA'});

// Create the map starting location and zoom level and tell it which layers to have

var map = L.map('map', {
    center: [48.46, -61.95],
    zoom: 6,
    layers: [light, streets]
});

// Create Lobster polygon layer

    // First parse JSON

const loadLobster = JSON.parse(document.getElementById('fa-data').textContent);

    // Then create the layer with name popup

function openUrl(feature) {

    // var url = "http://127.0.0.1:8000/en/fisheriescape/fisheryarea/" +str(feature.properties.id)+"/view/";
    // var url2 = "/view/";
    // var id = feature.properties.id;
    // var urls = url + id + url2;
    // window.open(url, '_self');

    window.open("http://127.0.0.1:8000/en/fisheriescape/fisheryarea/1/view/");
    // 'fisheryarea/<int:pk>/view/'
    // window.open("fisheriescape/fishery_area_detail");
    // window.location.href = "{% url 'fisheriescape:fishery_area_detail' object.id  %}";
}

function showInfo() {
    this.setStyle({
        'fillColor': '#689ae9'
    });
}

function removeInfo() {
    lobsterFishery.resetStyle(this);
    }


var lobsterFishery = L.geoJSON(loadLobster, {
    style: function() {
        return {
            color: 'blue'
        }
    },
    onEachFeature: function (feature, layer) {
        layer.bindPopup(feature.properties.name);
        layer.on({
            mouseover: showInfo,
            mouseout: removeInfo,
            click: openUrl
        });
        }
});

// Create basemaps variable and add basemaps desired to it as options

var baseMaps = {
    "Light": light,
    "Streets": streets
};

// Create overlay variable and add overlays desired

var overlayMaps = {
    "test": tests,
    "lobster areas": lobsterFishery
};

// Create the control layer box and add baseMaps and overlayMaps to it

L.control.layers(baseMaps, overlayMaps).addTo(map);