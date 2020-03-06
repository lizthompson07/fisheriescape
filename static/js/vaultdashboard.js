function processData(dataset) {
    var result = []
    dataset = JSON.parse(dataset);
    dataset.forEach(item => result.push(item.fields));
    return result;
}
$.ajax({
    url: $("#pivot-table-container").attr("data-url"),
    dataType: 'json',
    success: function(data) {
        new Flexmonster({
            container: "#pivot-table-container",
            componentFolder: "https://cdn.flexmonster.com/",
            width: "100%",
            height: 430,
            toolbar: true,
            report: {
                dataSource: {
                    type: "json",
                    data: processData(data),
                    mapping: {
                        "observation_platform": {
                            "caption": "Observation Platform"
                        },
                        "region": {
                            "caption": "Region"
                        },
                        "Purpose": {
                            "caption": "Purpose",
                        },
                        "Duration": {
                            "caption": "Duration",
                            "type": "number"
                        }
                    }
                },
                "slice": {
                    "rows": [{
                        "uniqueName": "observation_platform"
                    }],
                    "columns": [{
                            "uniqueName": "Region"
                        },
                        {
                            "uniqueName": "Purpose"
                        },
                        {
                            "uniqueName": "[Measures]"
                        }
                    ],
                    "measures": [{
                            "uniqueName": "Duration",
                            "aggregation": "sum"
                        }
                    ]
                }
            }
        });
        new Flexmonster({
            container: "#pivot-chart-container",
            componentFolder: "https://cdn.flexmonster.com/",
            width: "100%",
            height: 430,
            //toolbar: true,
            report: {
                dataSource: {
                    type: "json",
                    data: processData(data),
                    mapping: {
                        "observation_platform": {
                            "caption": "Observation Platform"
                        },
                        "region": {
                            "caption": "Region"
                        },
                        "Purpose": {
                            "caption": "Purpose",
                        },
                        "Duration": {
                            "caption": "Duration",
                            "type": "number"
                        }
                    }
                },
                "slice": {
                    "rows": [{
                        "uniqueName": "observation_platform"
                    }],
                    "columns": [{
                        "uniqueName": "[Measures]"
                    }],
                    "measures": [{
                        "uniqueName": "Duration",
                        "formula": "sum("Duration") + count("Duration")",
                        "caption": "Average Flight Duration"
                    }]
                },
                "options": {
                    "viewType": "charts",
                    "chart": {
                        "type": "pie"
                    }
                }
            }
        });
    }
});