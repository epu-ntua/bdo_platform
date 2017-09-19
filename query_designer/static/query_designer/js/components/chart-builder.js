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
            variable = undefined;

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

        // initially unknown chart type
        var chartType = new UnknownChart(that, nonVisualizedDimensions, {});

        // use map if coordinates are found
        if ((coordinateCols.latIdx !== undefined) && (coordinateCols.lngIdx !== undefined)) {
            chartType = new MapChart(that, nonVisualizedDimensions, {
                headers: headers,
                variable: variable,
                coordinateCols: coordinateCols
            })
        }

        /* Default - inform user no visualization was found */
        return {
            nonVisualizedDimensions: nonVisualizedDimensions,
            variable: variable,
            onHeadersLoaded: chartType.onHeadersLoaded,
            onChartCreated: chartType.onChartCreated,
            onFiltersUpdateStarted: chartType.onFiltersUpdateStarted,
            onFiltersUpdated: chartType.onFiltersUpdated,
            getGranularity: chartType.getGranularity,
            getVisualizationFilters: chartType.getVisualizationFilters
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
        var vDimensions = [];
        $.each(this.directives.nonVisualizedDimensions, function(idx, dim) {
            dim.values = that.headers[dim.idx].values;
            if (dim.values !== undefined) {
                vDimensions.push(dim);
            }
        });
        this.directives.nonVisualizedDimensions = vDimensions;

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