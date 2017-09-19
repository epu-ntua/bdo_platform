/**
 * Created by dimitris on 19/9/2017.
 */
MapChart = function(refChart, nonVisualizedDimensions, config) {
    var onHeadersLoaded = undefined,
        onFiltersUpdateStarted = undefined,
        onChartCreated = undefined,
        onFiltersUpdated = undefined,
        getGranularity = function() {return null},
        getVisualizationFilters = undefined,
        coordinateCols = config.coordinateCols,
        headers = config.headers,
        variable = config.variable;

    // we'll visualize map coords & value, all other dimensions are filterable
    $.each(headers, function(idx, col) {
        if ((coordinateCols.latIdx !== idx) && (coordinateCols.lngIdx !== idx) && (variable.idx !== idx) && (!col.isVariable)) {
            nonVisualizedDimensions.push({
                idx: idx,
                name: col.name,
                unit: col.unit,
                title: col.title,
                quote: col.quote
            })
        }
    });

    var mapCtx = null,
        $mapCanvas = null,
        results = undefined;

    var clearCanvas = function() {
        mapCtx.clearRect(0, 0, $mapCanvas.get(0).width, $mapCanvas.get(0).height);
    };

    var redrawCanvas = function(map) {
        var vDistribution = refChart.headers[variable.idx].distribution,
            latStep = 9999999,
            lngStep = 9999999;

        /* Find "typical" distance between two different points */
        var p1 = results[0];
        $.each(results, function(idx, r) {
            if (idx !== 0) {
                if (r[coordinateCols.latIdx] != p1[coordinateCols.latIdx]) {
                    latStep = Math.min(Math.abs(r[coordinateCols.latIdx] - p1[coordinateCols.latIdx]) * 1.1, latStep);
                }

                if (r[coordinateCols.lngIdx] != p1[coordinateCols.lngIdx]) {
                    lngStep = Math.min(Math.abs(r[coordinateCols.lngIdx] - p1[coordinateCols.lngIdx]) * 1.1, lngStep);
                }
            }
        });

        // update datapoint counter
        $('#query-visualization--container')
            .parent()
            .find('> .datapoint-counter')
            .text(results.length.toLocaleString() + ' datapoints');

        // redraw
        $.each(results, function(idx, r) {
            var loc = map.coordinatesToStageXY(r[coordinateCols.lngIdx], r[coordinateCols.latIdx]),
                compLoc = map.coordinatesToStageXY(r[coordinateCols.lngIdx] + lngStep, r[coordinateCols.latIdx] + latStep),
                difX = Math.max(Math.min(compLoc.x - loc.x, 10), 5),
                difY = Math.max(Math.min(compLoc.y - loc.y, 10), 5),
                v = r[variable.idx];

            mapCtx.beginPath();
            mapCtx.fillStyle = refChart.util.getColorFromDistribution(vDistribution, v);
            // mapCtx.arc(loc.x, loc.y, difX, 0, 2 * Math.PI);
            mapCtx.rect(loc.x - difX / 2.0, loc.y - difY / 2.0, difX, difY);
            mapCtx.fill();
        });
    };

    var updateRequests = [];

    onHeadersLoaded = function() {
        var $c = $('#query-visualization--container');

        $mapCanvas = $('<canvas />')
            .attr('id', 'query-visualization--map-canvas')
            .attr('width', $c.outerWidth())
            .attr('height', 500)
            .css('position', 'absolute')
            .css('left', '22px')
            .css('top', '95px');

        mapCtx = $mapCanvas.get(0).getContext("2d");

        // append map canvas
        $c.parent().append($mapCanvas);

        // add datapoint counter
        $c.parent().append($('<div />')
            .addClass('datapoint-counter')
            .css('position', 'absolute')
            .css('right', '20px')
            .css('top', '67px')
            .css('color', '#aaa')
        );

        refChart.chartConfig = {
            "type": "map",
            "theme": "light",
            "projection": "miller",

            "imagesSettings": {
                "rollOverColor": "#089282",
                "rollOverScale": 3,
                "selectedScale": 3,
                "selectedColor": "#089282",
                "color": "#13564e"
            },

            "dataProvider": {
                "map": "worldHigh"
            }
        };
    };

    onChartCreated = function() {
        var map = refChart.ui.chart;

        refChart.directives.getGranularity = function() {
            return Math.round(Math.max(8 - map.zoomLevel(), 1));
        };

        refChart.directives.getVisualizationFilters = function() {
            try {
                var zl = map.zoomLevel(),
                    info = map.getDevInfo(),
                    rect = {
                        lat: {
                            min: info.zoomLatitude - 90 / zl,
                            max: info.zoomLatitude + 90 / zl
                        },
                        lng: {
                            min: info.zoomLongitude - 180 / (zl * 0.75),
                            max: info.zoomLongitude + 180 / (zl * 0.75)
                        }
                    };

                return [
                    {"a": headers[coordinateCols.latIdx].name, "op": "gte", "b": rect.lat.min},
                    {"a": headers[coordinateCols.latIdx].name, "op": "lte", "b": rect.lat.max},
                    {"a": headers[coordinateCols.lngIdx].name, "op": "gte", "b": rect.lng.min},
                    {"a": headers[coordinateCols.lngIdx].name, "op": "lte", "b": rect.lng.max}
                ]
            } catch (e) {
                return []
            }
        };

        map.addListener("positionChanged", function() {
            var updateId = Date.now();
            updateRequests.push(updateId);
            clearCanvas();

            setTimeout(function() {
                if (updateRequests[updateRequests.length - 1] === updateId) {
                    if (results === undefined) {
                        clearCanvas();
                        redrawCanvas(map);

                        return
                    }

                    // update default visualization filters
                    refChart.filters.getFilteredResults(function(res) {
                        results = res;
                        updateRequests = [];
                        clearCanvas();
                        redrawCanvas(map, getGranularity());
                    });
                }
            }, 400);
        });
    };

    onFiltersUpdateStarted = function() {
        clearCanvas();
    };

    onFiltersUpdated = function(res, resetView, callback) {
        resetView = resetView || false;
        results = res;

        // no data
        var map = refChart.ui.chart;

        if (res.length > 0) {
            var latRange = refChart.getRangeFromData(results, coordinateCols.latIdx),
                lngRange = refChart.getRangeFromData(results, coordinateCols.lngIdx);
        }

        // at start, draw canvas
        clearCanvas();
        redrawCanvas(map);

        if (callback !== undefined) {
            callback();
        }
    };

    this.onHeadersLoaded = onHeadersLoaded;
    this.onChartCreated = onChartCreated;
    this.onFiltersUpdateStarted = onFiltersUpdateStarted;
    this.onFiltersUpdated = onFiltersUpdated;
    this.getVisualizationFilters = getVisualizationFilters;

    return this
};