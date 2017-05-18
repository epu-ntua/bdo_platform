/**
 * Created by dimitris on 16/5/2017.
 */

var ChartFilters = function(chartBuilder, results, filterColumns) {
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

                $.each(fc.filters, function(jdx, filter) {
                    var $option = $('<option />')
                        .attr('value', jdx)
                        .text(filter);

                    if (jdx === fc.activeFilterIdx) {
                        $option.attr('selected', 'selected');
                    }

                    $select.append($option);

                    // on filter change
                    $select.on('change', function() {
                        fc.activeFilterIdx = Number($(this).val());
                        that.chartBuilder.onDataUpdated();
                    });

                    // on play/pause click
                    $play.on('click', function() {
                        var stopPlaying = function() {
                            clearInterval(fc.playingTimer);
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
                                that.chartBuilder.onDataUpdated();
                                fc.activeFilterIdx++;
                                if (fc.activeFilterIdx + 1 >= fc.filters.length) {
                                    stopPlaying();
                                    fc.activeFilterIdx = 0;
                                }
                            };

                            fc.activeFilterIdx = 0;
                            fn();
                            fc.playingTimer = setInterval(fn, 1000);
                        } else {
                            stopPlaying();
                        }
                    });
                });

                that.ui.$elem.append($label);
                that.ui.$elem.append($select);
                that.ui.$elem.append($play)
            });

            $('#query-visualization--container').parent().prepend(this.$elem);
        }
    };

    /* Responsible to return only data that should be shown according to current filters */
    this.getFilteredResults = function() {
        var filteredResults = [];
        $.each(results, function(idx, result) {
           var res = true;
            $.each(that.filterColumns, function(jdx, fc) {
                if (result[fc.idx] !== fc.filters[fc.activeFilterIdx]) {
                    res = false;
                    return false
                }
            });

            if (res) {
                filteredResults.push(result);
            }
        });

        return filteredResults;
    };

    this.initializeFilters = function() {
        $.each(that.filterColumns, function(idx, fc) {
            fc.filters = [];
            fc.activeFilterIdx = 0;
            fc.playingTimer = null;
            $.each(results, function(jdx, result) {
                if (fc.filters.indexOf(result[fc.idx]) < 0) {
                    fc.filters.push(result[fc.idx])
                }
            });
            fc.filters.sort();
        });
    };

    // initialize
    this.initializeFilters();

    // render filters
    this.ui.render();

    return this
};


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
            this.chart = AmCharts.makeChart(this.containerId, that.directives.config);

            // run post-add action to add data
            that.directives.onChartCreated();
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
            nonVisualizedDimensions = [],
            onChartCreated = undefined,
            onDataUpdated = undefined;

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
            // we'll visualize map coords & value, all other dimensions are filterable
            $.each(data.headers.columns, function(idx, col) {
                if ((coordinateCols.latIdx !== idx) && (coordinateCols.lngIdx !== idx) && (variables[0].idx !== idx)) {
                    nonVisualizedDimensions.push({
                        idx: idx,
                        name: col.name,
                        unit: col.unit,
                        title: col.title
                    })
                }
            });

            var latRange = this.getRange(coordinateCols.latIdx),
                lngRange = this.getRange(coordinateCols.lngIdx),
                $c = $('#query-visualization--container'),
                $mapCanvas = $('<canvas />')
                    .attr('id', 'query-visualization--map-canvas')
                    .attr('width', $c.outerWidth())
                    .attr('height', 500)
                    .css('position', 'absolute')
                    .css('left', '22px')
                    .css('top', '95px'),
                mapCtx = $mapCanvas.get(0).getContext("2d");

            // append map canvas
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

            var clearCanvas = function() {
                mapCtx.clearRect(0, 0, $mapCanvas.get(0).width, $mapCanvas.get(0).height);
            };

            var redrawCanvas = function(map) {
                var zl = map.zoomLevel(),
                    rad = zl * 0.175;
                $.each(that.filters.getFilteredResults(), function(idx, r) {
                    /*
                    var infoText = "#" + (idx + 1);
                    $.each(data.headers.columns, function(idx, col) {
                        if ((idx !== coordinateCols.latIdx) && (idx !== coordinateCols.lngIdx)) {
                            infoText += '<p>' + data.headers.columns[idx].title + ':<br /><b>' + r[idx] + '</b></p>';
                        }
                    });
                    */

                    var loc = map.coordinatesToStageXY(r[coordinateCols.lngIdx], r[coordinateCols.latIdx]),
                        v = r[variables[0].idx];

                    mapCtx.beginPath();
                    mapCtx.fillStyle = that.util.getColorForPercentage((v - variables[0].range.min) / variables[0].range.max);
                    mapCtx.arc(loc.x + zl, loc.y, rad, 0, 2 * Math.PI);
                    mapCtx.fill();
                });
            };

            var updateRequests = [];
            onChartCreated = function() {
                var map = that.ui.chart;

                map.addListener("positionChanged", function() {
                    var updateId = Date.now();
                    updateRequests.push(updateId);
                    clearCanvas();

                    setTimeout(function() {if (updateRequests[updateRequests.length - 1] === updateId) {updateRequests = []; redrawCanvas(map)}}, 400);
                });
            };

            onDataUpdated = function() {
                var map = that.ui.chart;

                // at start, draw canvas
                clearCanvas();
                redrawCanvas(map);
            }
        }

        return {
            config: config,
            nonVisualizedDimensions: nonVisualizedDimensions,
            onChartCreated: onChartCreated,
            onDataUpdated: onDataUpdated
        }
    };

    // basic rendering
    this.ui.render();

    // choose visualization
    this.directives = this.pickVisualizationType();

    // setup filters
    this.filters = new ChartFilters(this, data.results, this.directives.nonVisualizedDimensions);

    // render chart
    this.ui.renderChart();

    // load initial data
    this.onDataUpdated = function() {
        this.directives.onDataUpdated();
    };

    this.onDataUpdated();

    return this;
};