/**
 * Created by dimitris on 16/5/2017.
 */
ChartBuilder = function(destSelector, data) {
    var that = this;

    this.util = {
        getColorForPercentage: function(pct) {
            if (pct === undefined) {
                return 'green';
            }

            var percentColors = [
                { pct: 0.0, color: { r: 0xff, g: 0x00, b: 0 } },
                { pct: 0.5, color: { r: 0xff, g: 0xff, b: 0 } },
                { pct: 1.0, color: { r: 0x00, g: 0xff, b: 0 } }];

            for (var i = 1; i < percentColors.length - 1; i++) {
                if (pct < percentColors[i].pct) {
                    break;
                }
            }
            var lower = percentColors[i - 1];
            var upper = percentColors[i];
            var range = upper.pct - lower.pct;
            var rangePct = (pct - lower.pct) / range;
            var pctLower = 1 - rangePct;
            var pctUpper = rangePct;
            var color = {
                r: Math.floor(lower.color.r * pctLower + upper.color.r * pctUpper),
                g: Math.floor(lower.color.g * pctLower + upper.color.g * pctUpper),
                b: Math.floor(lower.color.b * pctLower + upper.color.b * pctUpper)
            };
            return 'rgb(' + [color.r, color.g, color.b].join(',') + ')';
            // or output as hex if preferred
        }
    };

    this.ui = {
        $elem: undefined,
        $container: $(destSelector),

        render: function() {
            var containerId = 'query-visualization--container';
            this.$elem = $('<div />')
                .attr('id', containerId);

            // clear & create container
            this.$container
                .empty()
                .append(this.$elem);

            // choose visualization
            var directives = that.pickVisualizationType();

            // render visualization
            var chart = AmCharts.makeChart(containerId, directives.config);

            // run post-add actions (e.g map markers)
            if (directives.postAddAction !== undefined) {
                directives.postAddAction(chart);
            }
        }
    };

    /* Get range of values for a column */
    this.getRange = function(columnIdx) {
        var min = data.results[0][columnIdx],
            max = data.results[0][columnIdx];

        $.each(data.results, function(idx, r) {
            if (r[columnIdx] < min) {
                min = r[columnIdx]
            }
            else if (r[columnIdx] > max) {
                max = r[columnIdx]
            }
        });

        return {min: min, max: max};
    };

    /* Initial configuration for visualization type */
    this.pickVisualizationType = function() {
        var config = {},
            postAddAction = undefined;

        // find variable(s)
        var variables = [];
        $.each(data.headers.columns, function(idx, col) {
            if (col.unit === 'VALUE') {
                variables.push({
                    idx: idx,
                    range: that.getRange(idx)
                });
            }
        });

        // choose map if "degrees_north" & "degrees_east" units are present
        var coordinateCols = {latIdx: undefined, lngIdx: undefined};
        $.each(data.headers.columns, function(idx, col) {
            if (col.unit === 'degrees_north') {
               coordinateCols.latIdx = idx;
            }
            else if (col.unit === 'degrees_east') {
               coordinateCols.lngIdx = idx;
            }
        });

        if ((coordinateCols.latIdx !== undefined) && (coordinateCols.lngIdx !== undefined)) {
            var latRange = this.getRange(coordinateCols.latIdx),
                lngRange = this.getRange(coordinateCols.lngIdx),
                $c = $('#query-visualization--container'),
                $mapCanvas = $('<canvas />')
                    .attr('id', 'query-visualization--map-canvas')
                    .attr('width', $c.outerWidth())
                    .attr('height', 500)
                    .css('position', 'absolute')
                    .css('left', '22px')
                    .css('top', '69px'),
                mapCtx = $mapCanvas.get(0).getContext("2d");

            $c.parent().append($mapCanvas);

            // calculate default zoom level
            var latDiff = Math.abs(latRange.max - latRange.min),
                lngDiff = Math.abs(lngRange.max - lngRange.min),
                maxDiff = latDiff;
            if (maxDiff < lngDiff) {
                maxDiff = lngDiff;
            }

            var zoomLevel = 120.0 / maxDiff;
            if (zoomLevel > 15) {
                zoomLevel = 15;
            }

            config = {
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
                    "map": "worldHigh",
                    "zoomLevel": zoomLevel,
                    "zoomLatitude": (latRange.min + latRange.max) / 2,
                    "zoomLongitude": (lngRange.min + lngRange.max) / 2
                }
            };

            var updateRequests = [];
            postAddAction = function(map) {

                var clearCanvas = function() {
                    mapCtx.clearRect(0, 0, $mapCanvas.get(0).width, $mapCanvas.get(0).height);
                };

                var redrawCanvas = function() {
                    $.each(data.results, function(idx, r) {

                        var loc = map.coordinatesToStageXY(r[coordinateCols.lngIdx], r[coordinateCols.latIdx]),
                            v = r[variables[0].idx];

                        mapCtx.beginPath();
                        mapCtx.fillStyle = that.util.getColorForPercentage((v - variables[0].range.min) / variables[0].range.max);
                        mapCtx.arc(loc.x + 2, loc.y + 2, zoomLevel, 0, 2 * Math.PI);
                        mapCtx.fill();
                    });
                };

                map.addListener("positionChanged", function() {
                    var updateId = Date.now();
                    updateRequests.push(updateId);
                    clearCanvas();

                    setTimeout(function() {if (updateRequests[updateRequests.length - 1] === updateId) {updateRequests = []; redrawCanvas()}}, 400);
                });
            };

            /*
            // add data
            $.each(data.results, function(idx, r) {
                var infoText = "#" + (idx + 1);
                $.each(data.headers.columns, function(idx, col) {
                    if ((idx !== coordinateCols.latIdx) && (idx !== coordinateCols.lngIdx)) {
                        infoText += '<p>' + data.headers.columns[idx].title + ':<br /><b>' + r[idx] + '</b></p>';
                    }
                });

                var v = r[variables[0].idx];
                config.dataProvider.images.push({
                    "zoomLevel": zoomLevel,
                    "scale": 0.5,
                    "text": infoText,
                    "latitude": r[coordinateCols.latIdx],
                    "longitude": r[coordinateCols.lngIdx],
                    "value": v,
                    "valuePerc": (v - variables[0].range.min) / variables[0].range.max
                });
            });

            // add custom markers
            // add events to recalculate map position when the map is moved or zoomed
            postAddAction = function(map) {

                // this function will take current images on the map and create HTML elements for them
                var updateCustomMarkers = function( event ) {
                    // get map object
                    var map = event.chart;

                    // go through all of the images
                    for ( var x in map.dataProvider.images ) {
                        // get MapImage object
                        var image = map.dataProvider.images[ x ];

                        // check if it has corresponding HTML element
                        if ( 'undefined' == typeof image.externalElement ) {
                            image.externalElement = createCustomMarker(image,
                                that.util.getColorForPercentage(image.valuePerc));
                        }

                        // reposition the element accoridng to coordinates
                        var xy = map.coordinatesToStageXY( image.longitude, image.latitude );
                        image.externalElement.style.top = xy.y + 'px';
                        image.externalElement.style.left = xy.x + 'px';
                    }
                };

                // this function creates and returns a new marker element
                var createCustomMarker = function(image, color) {
                    // create holder
                    var holder = document.createElement( 'div' );
                    holder.className = 'map-marker';
                    holder.style.background = color;

                    // maybe add a link to it?
                    if (image.url !== undefined) {
                        holder.onclick = function() {
                            window.location.href = image.url;
                        };
                        holder.className += ' map-clickable';
                    }

                    // add info
                    var info = document.createElement( 'div' );
                    info.className = 'info';
                    info.innerHTML = image.text;
                    holder.appendChild(info);

                    // append the marker to the map container
                    that.ui.$elem.append( holder );

                    return holder;
                };

                map.addListener("positionChanged", updateCustomMarkers);
            }
            */
        }

        return {
            config: config,
            postAddAction: postAddAction
        }
    };

    this.ui.render();

    return this;
};