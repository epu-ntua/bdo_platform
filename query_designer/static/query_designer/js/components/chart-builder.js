/**
 * Created by dimitris on 16/5/2017.
 */

var ChartFilters = function(chartBuilder, filterColumns) {
    var that = this;
    this.chartBuilder = chartBuilder;
    this.filterColumns = filterColumns;

    this.ui = {
        $elem: undefined,

        // renders all visualization filters
        render: function() {
            this.$elem = $('<div />').addClass('visualization-filters');
            $.each(that.filterColumns, function(idx, fc) {

                var selectName = 'visualization-filter--' + fc.name,
                    $label = $('<label />').attr('for', selectName).text(fc.title),
                    $select = $('<select />').attr('name', selectName),
                    $play = $('<i />').addClass('material-icons text-green').text('play_arrow');

                $.each(fc.values, function(jdx, filter) {
                    var $option = $('<option />')
                        .attr('value', jdx)
                        .text(filter);

                    if (jdx === fc.activeFilterIdx) {
                        $option.attr('selected', 'selected');
                    }

                    $select.append($option);
                });

                // on filter change
                $select.on('change', function() {
                    fc.activeFilterIdx = Number($(this).val());
                    that.chartBuilder.onFiltersUpdated();
                });

                // on play/pause click
                $play.on('click', function() {
                    var stopPlaying = function() {
                        clearTimeout(fc.playingTimer);
                        fc.playingTimer = null;
                        $play.text('play_arrow').removeClass('text-orange').addClass('text-green');
                    };

                    if (fc.playingTimer !== null) {
                        $play.text('play_arrow').removeClass('text-orange').addClass('text-green');
                    } else {
                        $play.text('pause_arrow').removeClass('text-green').addClass('text-orange');
                    }

                    if (fc.playingTimer === null) {
                        var fn = function() {
                            that.chartBuilder.onFiltersUpdated({
                                ignoreOnStarted: true,
                                afterRedraw: function() {
                                    $select.get(0).selectedIndex = fc.activeFilterIdx;

                                    // detect if stopped in the mean time
                                    if (fc.playingTimer === null) {
                                        return
                                    }

                                    if (fc.activeFilterIdx + 1 >= fc.values.length) {
                                        stopPlaying();
                                    } else {
                                        fc.activeFilterIdx++;
                                        fc.playingTimer = setTimeout(fn, 1000);
                                    }
                                }
                            });
                        };

                        fc.activeFilterIdx = 0;
                        fc.playingTimer = setTimeout(fn, 10);
                    } else {
                        stopPlaying();
                    }
                });

                that.ui.$elem.append($label);
                that.ui.$elem.append($select);
                that.ui.$elem.append($play)
            });

            $('#query-visualization--container').parent().prepend(this.$elem);
        }
    };

    /* Responsible to return only data that should be shown according to current filters */
    this.getFilteredResults = function(callback) {
        var extraFilters = undefined;

        // update datapoint counter
        $('#query-visualization--container')
            .parent()
            .find('> .datapoint-counter')
            .html('<i class="fa fa-spin fa-spinner"></i> Loading visualization data');

        // add filters from visualizations
        $.each(that.filterColumns, function(idx, filter) {
            var value = filter.values[filter.activeFilterIdx];
            if (filter.quote !== undefined) {
                value = filter.quote + value + filter.quote;
            }

            var fObj = {
                "a": filter.name,
                "op": "EQ",
                "b": value + ''
            };
            if (extraFilters === undefined) {
                extraFilters = fObj
            } else {
                extraFilters = {
                    "a": JSON.parse(JSON.stringify(extraFilters)),
                    "op": "AND",
                    "b": fObj
                }
            }
        });

        // add visualization drilldowns
        $.each(that.chartBuilder.directives.getVisualizationFilters(), function(idx, fObj) {
            if (extraFilters === undefined) {
                extraFilters = fObj
            } else {
                extraFilters = {
                    "a": JSON.parse(JSON.stringify(extraFilters)),
                    "op": "AND",
                    "b": fObj
                }
            }
        });

        // execute the query
        that.chartBuilder.qd.queryExecutor.run({
            noPagination: true,
            extraFilters: extraFilters,
            granularity: that.chartBuilder.directives.getGranularity(),
            callback: function(data) {
                callback(data.results);
            }
        });
    };

    this.initializeFilters = function() {
        $.each(that.filterColumns, function(idx, fc) {
            fc.activeFilterIdx = 0;
            fc.playingTimer = null;
        });
    };

    // initialize
    this.initializeFilters();

    // render filters
    this.ui.render();

    return this
};


ChartLegend = function(title, unit, legendValues) {
    /* Generates a legend given an array of legend value entries
    * {color, min, max}
    * */
    var that = this;

    this.ui = {
        $elem: undefined,

        render: function() {
            if (this.$elem === undefined) {
                this.$elem = $('<div />')
                    .addClass('visualization-legend');
            }

            this.$elem.empty();

            // add title
            this.$elem.append($('<h5 />')
                .addClass('o-blue')
                .text(title + ((unit !== title)?' (' + unit + ')':''))
            );

            // add legend
            var $contents = $('<div />')
                .addClass('visualization-legend--contents');

            $.each(legendValues, function(idx, legendValue) {
                $contents.append($('<div />')
                    .addClass('visualization-legend--item')
                    .append($('<div />')
                        .css('background', legendValue.color)
                    )
                    .append($('<span />')
                        .text(legendValue.min + ' - ' + legendValue.max)
                    )
                );
            });

            this.$elem.append($contents);
        }
    };

    this.ui.render();

    return this
};


ChartBuilder = function(qd, destSelector, headers) {
    var that = this;
    this.qd = qd;
    this.headers = headers;
    this.chartConfig = undefined;

    this.util = {
        getRGBForPercentage: function(pct, percentColors) {
            if (pct === undefined) {
                return 'green';
            }

            percentColors = percentColors || [
                { pct: 0.0, color: { r: 0xff, g: 0x00, b: 0 } },
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
            return {
                r: Math.floor(lower.color.r * pctLower + upper.color.r * pctUpper),
                g: Math.floor(lower.color.g * pctLower + upper.color.g * pctUpper),
                b: Math.floor(lower.color.b * pctLower + upper.color.b * pctUpper)
            };
        },

        RGBToHex: function(rgbColor) {
            return 'rgb(' + [rgbColor.r, rgbColor.g, rgbColor.b].join(',') + ')'
        },

        getColorForPercentage: function(pct) {
            return this.RGBToHex( this.getRGBForPercentage(pct) );
        },

        getColorFromDistribution: function(distribution, v) {
            var colors = [
                this.getRGBForPercentage(0),
                this.getRGBForPercentage(0.10),
                this.getRGBForPercentage(0.25),
                this.getRGBForPercentage(0.50),
                this.getRGBForPercentage(0.75),
                this.getRGBForPercentage(0.90),
                this.getRGBForPercentage(1)
            ];

            // find the correct distribution segment & interpolate there
            for (var i=0; i<distribution.length - 1; i++) {
                if ((v >= distribution[i]) && (v < distribution[i + 1])) {
                    var perc = (v -  distribution[i]) / (distribution[i + 1] - distribution[i]);
                    return this.RGBToHex( this.getRGBForPercentage(perc, [
                        { pct: 0.0, color: colors[i] },
                        { pct: 1.0, color: colors[i + 1] }
                    ]) );
                }
            }

            return 'green'
        }
    };

    this.ui = {
        $elem: undefined,
        $container: $(destSelector),
        chart: undefined,
        containerId: 'query-visualization--container',

        render: function() {
            this.$elem = $('<div />')
                .attr('id', this.containerId);

            // clear & create container
            this.$container
                .empty()
                .append(this.$elem);
        },

        renderChart: function() {
            // render visualization
            if (that.chartConfig !== undefined) {
                this.chart = AmCharts.makeChart(this.containerId, that.chartConfig);
            } else {
                this.$elem.append($('<p>').text('Data can\'t be visualized'));
            }

            // add legend
            var v = that.headers[that.directives.variable.idx],
                legendValues = [],
                ps = [0.00, 0.10, 0.25, 0.5, 0.75, 0.90, 1.00];

            $.each(ps, function(idx, p) {
                if ((idx > 0) && (idx < ps.length - 1)) {
                    legendValues.push({
                        min: v.distribution[idx],
                        max: v.distribution[idx + 1],
                        color: that.util.getColorForPercentage(p)
                    });
                }
            });
            var legend = new ChartLegend(v.title, v.unit, legendValues);
            this.$elem.parent().append(legend.ui.$elem);

            // run post-add action to add data
            that.directives.onChartCreated();
        }
    };

    /* Get range of values for a column */
    this.getRange = function(columnIdx) {
        return {
            min: this.headers[columnIdx].values[ 0 ],
            max: this.headers[columnIdx].values[ this.headers[columnIdx].length - 1 ]
        };
    };

    /* Get range of values for a column from data */
    this.getRangeFromData = function(data, columnIdx) {
        var min = data[0][columnIdx],
            max = data[0][columnIdx];

        $.each(data, function(idx, r) {
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
        var nonVisualizedDimensions = [],
            variable = undefined,
            onHeadersLoaded = undefined,
            onFiltersUpdateStarted = undefined,
            onChartCreated = undefined,
            onFiltersUpdated = undefined,
            getGranularity = function() {return null},
            getVisualizationFilters = undefined;

        // find variable(s)
        var variables = [];
        $.each(headers, function(idx, col) {
            if (col.isVariable) {
                variables.push({
                    idx: idx,
                    name: col.name
                });
            }
        });

        variable = variables[0];

        // choose map if "degrees_north" & "degrees_east" units are present
        var coordinateCols = {latIdx: undefined, lngIdx: undefined};
        $.each(headers, function(idx, col) {
            if (['degrees_north', 'degree_north'].indexOf(col.unit) >= 0) {
               coordinateCols.latIdx = idx;
            }
            else if (['degrees_east', 'degree_east'].indexOf(col.unit) >= 0) {
               coordinateCols.lngIdx = idx;
            }
        });

        if ((coordinateCols.latIdx !== undefined) && (coordinateCols.lngIdx !== undefined)) {
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
                var vDistribution = that.headers[variable.idx].distribution,
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
                        difX = Math.max(Math.min(compLoc.x - loc.x, 10), -10),
                        difY = Math.max(Math.min(compLoc.y - loc.y, 10), -10),
                        v = r[variable.idx];

                    mapCtx.beginPath();
                    mapCtx.fillStyle = that.util.getColorFromDistribution(vDistribution, v);
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

                that.chartConfig = {
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
                var map = that.ui.chart;

                that.directives.getGranularity = function() {
                    return Math.round(Math.max(8 - map.zoomLevel(), 1));
                };

                that.directives.getVisualizationFilters = function() {
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
                            {"a": headers[coordinateCols.lngIdx].name, "op": "lte", "b": rect.lng.max},
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
                            that.filters.getFilteredResults(function(res) {
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
                var map = that.ui.chart,
                    latRange = that.getRangeFromData(results, coordinateCols.latIdx),
                    lngRange = that.getRangeFromData(results, coordinateCols.lngIdx);

                // calculate default zoom level
                /*var latDiff = Math.abs(latRange.max - latRange.min),
                    lngDiff = Math.abs(lngRange.max - lngRange.min),
                    maxDiff = latDiff;
                if (maxDiff < lngDiff) {
                    maxDiff = lngDiff;
                }

                var zoomLevel = 120.0 / maxDiff;
                if (zoomLevel > 15) {
                    zoomLevel = 15;
                }

                if (resetView) {
                    map.dataProvider.zoomLevel = zoomLevel;
                    map.dataProvider.zoomLatitude =  (latRange.min + latRange.max) / 2;
                    map.dataProvider.zoomLongitude = (lngRange.min + lngRange.max) / 2;
                    map.validateData();
                }*/

                // at start, draw canvas
                clearCanvas();
                redrawCanvas(map);

                if (callback !== undefined) {
                    callback();
                }
            }
        } else {
            onHeadersLoaded = function() {};
            onChartCreated = function() {};
            onFiltersUpdateStarted = function() {};
            onFiltersUpdated = function() {};
            getVisualizationFilters = function() {return []};
        }

        /* Default - inform user no visualization was found */
        return {
            nonVisualizedDimensions: nonVisualizedDimensions,
            variable: variable,
            onHeadersLoaded: onHeadersLoaded,
            onChartCreated: onChartCreated,
            onFiltersUpdateStarted: onFiltersUpdateStarted,
            onFiltersUpdated: onFiltersUpdated,
            getGranularity: getGranularity,
            getVisualizationFilters: getVisualizationFilters
        }
    };

    // basic rendering
    this.ui.render();

    // choose visualization
    this.directives = this.pickVisualizationType();

    // run query just to get headers
    var dimensionValues = [];
    $.each(this.directives.nonVisualizedDimensions, function(idx, dim) {
        dimensionValues.push(dim.name);
    });

    that.qd.queryExecutor.run({
        onlyHeaders: true,
        variable: that.directives.variable.name,
        dimensionValues: dimensionValues.join(','),
        noPagination: true,
        callback: function(data) {
            // update headers
            that.headers = data.headers.columns;
            that.onHeadersLoaded();
        }
    });

    // on filter update
    this.onFiltersUpdated = function(options) {
        options = $.extend({}, {
            updateView: false,
            ignoreOnStarted: false,
            afterRedraw: undefined
        }, options);

        if (!options.ignoreOnStarted) {
            that.directives.onFiltersUpdateStarted();
        }

        that.filters.getFilteredResults(function(results) {
            that.directives.onFiltersUpdated(results, options.updateView, function() {
                if (options.afterRedraw !== undefined) {
                    options.afterRedraw();
                }
            });
        });
    };

    // base rendering
    this.ui.render();

    this.onHeadersLoaded = function() {
        // complete config
        this.directives.onHeadersLoaded();

        // update non visualized dimensions
        $.each(this.directives.nonVisualizedDimensions, function(idx, dim) {
            dim.values = that.headers[dim.idx].values;
        });

        // setup filters
        this.filters = new ChartFilters(this, this.directives.nonVisualizedDimensions);

        // render chart
        this.ui.renderChart();

        // load initial data
        this.onFiltersUpdated({
            updateView: true
        });
    };

    return this;
};