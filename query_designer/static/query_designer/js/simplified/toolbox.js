$(function () {
    /* `QueryToolbox` is the object responsible for the behaviour of the Toolbox Charts component */
    var QueryToolbox = {
        objects: [],

        current: function () {
            return $('#chart-picker li.active').index();
        },

        /* Add a new chart */
        addChart: function (chartOptions, chartFilters, chartPolicy, chartId, chartTitle) {
            // save previous chart options & filters
            QueryToolbox.saveChartInfo();

            var chartTitle = chartTitle || 'Chart ' + ($('#chart-picker li').length + 1);

            this.chart = $('<iframe />');

            // save
            var obj = {
                'chartId': chartId,
                'chartTitle': chartTitle
            };
            this.objects.push(obj);

            // add tab
            $('#chart-picker').find('li').removeClass('active');
            $('#chart-picker').append('<li class="active"><a href="#chart-container"><span class="chartTitle">' + chartTitle + '</span> <i class="fa fa-times close-tab"></i></a></li>');

            // mark tab as unsaved for new charts
            if (typeof(chartId) === 'undefined') {
                this.tabMarker.currentUnsaved();
            }

            // set chart options (category/value fields) & filters
            if (typeof(chartOptions) === 'undefined') {
                this.initChartOptions(obj);
            } else {
                this.setChartOptions(obj, chartOptions, chartFilters, chartPolicy);
            }

            // show name field
            $('#chart-name').removeClass('hidden').find('input').val(chartTitle);

            // show graph
            $('#chartdiv')
                .empty()
                .append(this.chart);
        },

        setChartOptions: function (obj, chartOptions, chartFilters, chartPolicy) {
            obj.chartOptions = chartOptions;
            obj.$chartFilters = $(chartFilters);
            obj.chartPolicy = chartPolicy;

            this.renderChartOptions(obj);

            // render default graph
            this.fetchChartData();
        },

        /* Load default controls for this chart type/format */
        initChartOptions: function (obj) {
            var that = this;
            $.ajax({
                url: '/queries/simplified/config/',
                success: function (chartPolicy) {
                    var chartOptions = {
                        group: {
                            metric: chartPolicy.categories[0].value
                        },
                        fields: []
                    };

                    for (var j = 0; j < chartPolicy.incrStep; j++) {
                        chartOptions.fields.push({
                            metric: chartPolicy.valueFields[0].value
                        })
                    }

                    that.setChartOptions(obj, chartOptions, '', chartPolicy)
                }
            })
        },

        /* Refresh chart value fields */
        refreshValueFields: function () {
            if (typeof(this.current()) === 'undefined') {
                return
            }

            var obj = this.objects[this.current()];

            // fetch updated options from server
            var that = this;

            $.ajax({
                url: '/toolbox/util/graphControl/?chartType=' + encodeURIComponent(obj.chartType) + '&chartFormat=' + encodeURIComponent(obj.chartFormat),
                success: function (chartPolicy) {
                    obj.chartPolicy.valueFields = chartPolicy.valueFields;

                    // update the UI
                    $.each($('select[name="value_field"]'), function(idx, select) {
                        var $select = $(select),
                            val = $select.val();

                        $select.find('> option[value!=""]').remove();
                        $.each(obj.chartPolicy.valueFields, function(idx, valueField) {
                            var $option = $('<option />');

                            $option.attr('value', valueField.value);
                            $option.text(valueField.title);
                            $select.append($option)
                        });

                        $select.val(val).trigger('change.select2');
                    })
                }
            });
        },

        /* Creates an option (group or metric) fieldset */
        renderChartOptionsField: function (config) {
            // create select
            var $fieldSelect = $('<select name="' + config.name + '" />"');
            if (config.id) {
                $fieldSelect.attr('id', config.id);
            }

            if (typeof(config.aggregate) !== 'undefined') {
                var $aggregateSelect = $('<select name="field_aggregate" />');
                $.each(config.aggregates, function(idx, aggregate) {
                    // create aggregate option
                    var $option = $('<option />').text(aggregate.title).attr('value', aggregate.value);
                    if (config.aggregate === aggregate.value) {
                        $option.attr('selected', 'selected');
                    }

                    // add to aggregate select
                    $aggregateSelect.append($option);
                });

                // set initial aggregate
                $aggregateSelect.val(config.aggregate);
                $fieldSelect.attr('data-aggregate', config.aggregate);
                $fieldSelect.data('aggregate', config.aggregate);
            }

            if (config.emptyChoice) {
                $fieldSelect.append('<option value="">No value</option>');
            }

            $.each(config.choices, function (idx, choice) {
                var $option = $('<option />');

                $option.attr('value', choice.value);
                $option.text(choice.title);
                if (typeof(choice.type) !== 'undefined') {
                    $option.data('type', choice.type);
                    $option.attr('data-type', choice.type);
                }
                if (typeof(choice.forVariable) !== 'undefined') {
                    $option.data('forvariable', choice.forVariable);
                    $option.attr('data-forvariable', choice.forVariable);
                }

                $fieldSelect.append($option);
            });

            // set field value
            $fieldSelect.val(config.value);
            var $fieldset = $('<div class="fieldset">' + config.label + ': <br><div class="row"><div class="col-xs-3 col-prefix"></div><div class="col-xs-8 col-main"></div><div class="col-xs-1 col-suffix"></div></div></div>');
            $fieldset.find('.col-main').append($fieldSelect);

            if (config.xy) {
                $fieldset.addClass('xy')
            }

             if (typeof(config.aggregate) !== 'undefined') {
                $fieldset.find('.col-prefix').append($aggregateSelect);
            }

            if (config.canDelete) {
                $fieldset.find('.col-suffix').append('<div class="value-remove-btn" title="Remove value"><i class="fa fa-trash" /></div>')
            }

            return $fieldset;
        },

        /* renders the chart options & filters UI components */
        renderChartOptions: function (obj) {
            var $controlList = $('#chart-control-list');
            var $chartControls = $('<div class="chart-control" />');
            var defaultAggregate = obj.chartPolicy.defaultAggregate;

            /* empty from previous controls */
            $controlList.empty();

            /* load group */
            // create group select
            var $groupSelectContainer = this.renderChartOptionsField({
                choices: obj.chartPolicy.categories,
                name: 'category',
                id: 'id_category',
                label: 'Groups',
                value: obj.chartOptions.group.metric
            });
            $chartControls.append($groupSelectContainer);

            /* load fields */
            var that = this;
            $.each(obj.chartOptions.fields, function (idx, field) {
                var suffix = '',
                    cnt = (idx + 1),
                    value = field.metric;

                if (obj.chartType == 'xy/scatter/bubble') {
                    cnt = Math.floor(idx / 3) + 1;
                    if (idx % 3 == 0) {
                        suffix += ' (X axis)'
                    }
                    else if (idx % 3 == 1) {
                        suffix += ' (Y axis)'
                    } else {
                        suffix += ' (value)';
                        value = '';
                        defaultAggregate = 'AVG';
                    }
                }

                var label = 'Metric #<span class="metric-cnt">' + cnt + '</span>' + suffix;

                if (typeof(field.aggregate) === 'undefined') {
                    field.aggregate = defaultAggregate;
                }

                var $fieldset = that.renderChartOptionsField({
                    choices: obj.chartPolicy.valueFields,
                    emptyChoice: (obj.chartType == 'xy/scatter/bubble') && (idx % 3 == 2),
                    name: 'value_field',
                    label: label,
                    value: value,
                    aggregate: field.aggregate,
                    aggregates: obj.chartPolicy.aggregates,
                    canConfig: obj.chartPolicy.canConfig,
                    canDelete: idx + 1 > obj.chartPolicy.min,
                    xy: obj.chartType == "xy/scatter/bubble"
                });
                $chartControls.append($fieldset);
            });

            // append the whole list
            $controlList.append($chartControls);

            /* load filters */
            var $chartFilters = $('#chart-filters');

            // empty from previous filters
            $chartFilters.empty();
            $chartFilters.append(obj.$chartFilters);

            // add add filter & draw buttons
            var $btnContainer = $('<div class="row btn-container">').css('padding', '0 4px');
            if (obj.chartOptions.fields.length + 1 < obj.chartPolicy.max) {
                $btnContainer.append('<div class="add-value-field add-value-field btn btn-default btn-sm pull-left"><i class="fa fa-plus"></i> Add value</div>')
            }

            $btnContainer.append('<div class="btn btn-sm btn-primary pull-right fetch-graph-data"><i class="fa fa-line-chart"></i> Draw</div>');
            $controlList.append($btnContainer);

            // show filters button & apply plugin
            $('.filter-edit-open').show();
            $controlList.find('select').select2();

            this.filterManager.updateFilterCounter();
        },

        /* Store in memory chart options & filters */
        saveChartInfo: function () {
            var current = this.current();
            // if a graph is currently shown
            if (current >= 0) {
                // get chart options & filters
                var chartOptions = {
                    group: {
                        metric: $('#id_category').val()
                    },
                    fields: []
                };
                $.each($('select[name="value_field"]'), function (idx, select) {
                    var $select = $(select);
                    chartOptions.fields[idx] = {
                        metric: $select.val(),
                        aggregate: $select.data('aggregate')
                    }
                });
                var $chartFilters = $('#chart-filters').clone();

                // save controls
                this.objects[current].chartOptions = chartOptions;
                this.objects[current].$chartFilters = $chartFilters;
            }
        },

        getFilterArray: function () {
            var filters = [];
            $.each($('#chart-filters > .filter'), function (idx, flt) {
                var $flt = $(flt);
                filters.push({
                    'name': $flt.data('name'),
                    'title': $flt.data('title'),
                    'value': $flt.text()
                });
            });

            return filters
        },

        constructFiltersParam: function () {
            // gather individual filters
            var filters = this.getFilterArray();

            if (filters.length == 0) {
                return '';
            }

            // find pattern
            var $filterExpr = $('#chart-filters > .filter-expr');
            var exprType = $filterExpr.data('expr_type');
            var filterStr = '';
            if (exprType == 'ALL_AND' || exprType == 'ALL_OR') {
                var bln = exprType.split('_')[1];
                for (var i = 0; i < filters.length; i++) {
                    if (i > 0) {
                        filterStr += bln + ' ';
                    }
                    filterStr += filters[i].name + ' ';
                }
            } else {
                filterStr = $filterExpr.data('expr');
            }

            // apply named expressions to pattern & encode
            for (var i = 0; i < filters.length; i++) {
                filterStr = filterStr.replace(filters[i].name + ' ', '(' + filters[i].value + ')');
            }

            return filterStr
        },

        _getChartInfo: function () {
            var values = [], columns = [];
            var vfs = $('select[name="value_field"]');

            $.each(vfs, function (idx, vf) {
                // create the field name (including the aggregate)
                var aggregate = $(vf).data('aggregate');
                // if aggregate property was not found
                if (typeof(aggregate) === "undefined") {
                    aggregate = 'AVG'
                }

                var fname = $(vf).val();

                values.push({
                    name: fname,
                    type: $(vf).find('option:selected').data('type'),
                    aggregate: aggregate
                });

                // field title
                var ttl_prefix = '';
                if (aggregate != '') {
                    ttl_prefix = $('select[name="field_aggregate"] option[value="' + aggregate + '"]').get(0).textContent + ' '
                }
                var ttl = ttl_prefix + $(vf).find('option:selected').text();

                // keep the title of the field for the data table
                columns.push({name: fname, title: ttl});
            });

            return {
                values: values,
                columns: columns
            };
        },

        _constructGraph: function (fields) {
            var obj = this.objects[this.current()];
            var that = this;
            var valueAxesMap = {}, valueAxes = [];
            var ui = 0;

            this.chart.valueAxes = undefined;
            $.each(Object.keys(fields), function (idx, field) {
                if ((field == 'number_of_projects') || (field == 'total_projects')) {
                    return
                }

                var u = fields[field];
                if (!(u in valueAxesMap)) {
                    ui++;

                    var position = "left";
                    if (ui % 2 == 0) {
                        position = "right"
                    }

                    var axis = {
                        "id": "v" + ui,
                        "title": u,
                        "axisThickness": 1,
                        "axisAlpha": 1,
                        "position": position,
                        "offset": Math.floor((ui - 1) / 2) * 80
                    };
                    valueAxesMap[u] = axis;
                    valueAxes.push(axis);
                }
            });

            if ((obj.chartType == 'column') || (obj.chartType == 'bar') || (obj.chartType == 'line') || (obj.chartType == 'area') || (obj.chartType == 'pie & donut') || obj.chartType == 'other charts' || obj.chartType == 'xy/scatter/bubble') {
                var ct = $('select[name="category"]').val();
                var vfs = $('select[name="value_field"]');

                var values = [];

                this.chart.graphs = [];
                this.chart.valueAxes = [];

                var openField = '';
                var bulletStyles = ['round', 'square', 'triangle', 'diamond'];
                $.each(vfs, function (idx, vf) {
                    // create the field name (including the aggregate)
                    var aggregate = $(vf).data('aggregate');
                    // if aggregate property was not found
                    if (typeof(aggregate) === "undefined") {
                        aggregate = 'AVG'
                    }

                    if (obj.chartFormat == 'candlestick') {
                        aggregate = ''
                    }
                    var fname = $(vf).val();
                    if (aggregate != '') {
                        fname += '.' + aggregate
                    }

                    values.push(fname);

                    // number of projects info
                    var number_of_projects_info = '<br /> Number of projects' + ': [[number_of_projects]]';

                    // create the chart options
                    if ((obj.chartType == 'xy/scatter/bubble') && (idx % 3 == 2)) {
                        var cnt = ((idx - 2) / 3);
                        var x = values[idx - 2];
                        var xTitle = $(vfs[idx - 2]).find('option:selected').text();
                        var y = values[idx - 1];
                        var yTitle = $(vfs[idx - 1]).find('option:selected').text();
                        var v = values[idx];
                        var vTitle = $(vfs[idx]).find('option:selected').text();

                        var balloonText = xTitle + ":<b>[[x]]</b><br> " + xTitle + ":<b>[[y]]</b>";
                        if (vTitle != 'No value') {
                            balloonText += "<br>" + vTitle + ":<b>[[value]]</b>" + number_of_projects_info
                        }

                        var v2 = $(vfs[idx - 2]).val();
                        var aggr = $(vfs[idx - 2]).data('aggregate');
                        if (aggr) {
                            v2 += '.' + aggr
                        }
                        var v1 = $(vfs[idx - 1]).val();
                        aggr = $(vfs[idx - 1]).data('aggregate');
                        if (aggr) {
                            v1 += '.' + aggr
                        }

                        var g = {
                            "balloonText": balloonText,
                            "bullet": bulletStyles[cnt % bulletStyles.length],
                            "id": "AmGraph-" + cnt,
                            "lineAlpha": 0,
                            "bulletSize": 2,
                            "valueField": v,
                            "xField": x,
                            "yField": y,
                            "xValueAxis": valueAxesMap[fields[v2]].id,
                            "yValueAxis": valueAxesMap[fields[v1]].id
                        };

                        if (obj.chartFormat == "markers and lines" || obj.chartFormat == "with lines") {
                            g.lineAlpha = 1;
                            if (obj.chartFormat == "with lines") {
                                g.bulletAlpha = 0
                            }
                        } else if (obj.chartFormat == "zoom and scroll") {
                            g.chartCursor = {
                                "enabled": true
                            };
                            g.chartScrollbar = {
                                "enabled": true
                            }
                        } else if (obj.chartFormat == "fills") {
                            g.fillAlphas = 0.49;
                            g.bulletAlpha = 0
                        }

                        that.chart.graphs.push(g)
                    }
                    else if ((obj.chartType == 'column') || (obj.chartType == 'bar') || (obj.chartType == 'line') || (obj.chartType == 'area') || (obj.chartFormat == 'candlestick')) {
                        // field title
                        var ttl_prefix = '';
                        if (aggregate != '') {
                            ttl_prefix = $('select[name="field_aggregate"] option[value="' + aggregate + '"]').get(0).textContent + ' '
                        }
                        var ttl = ttl_prefix + $(vf).find('option:selected').text();

                        var graphConfig = {
                            "balloonText": "[[title]] of [[category]]: <b>[[value]]</b> " + fields[fname] + number_of_projects_info,
                            "id": "AmGraph-" + idx,
                            "title": ttl,
                            "valueAxes": []
                        };

                        if (obj.chartFormat != 'candlestick') {
                            graphConfig.valueAxis = valueAxesMap[fields[fname]].id
                        }

                        if (obj.chartFormat == 'clustered and stacked' && idx == 2) {
                            graphConfig.newStack = true;
                        }

                        if (obj.chartFormat == 'floating columns' || obj.chartFormat == 'floating bars') {
                            graphConfig.stackType = "regular";
                            if (idx == 0) {
                                openField = fname;
                            } else {
                                graphConfig.closeField = fname;
                                graphConfig.openField = openField;
                            }
                        } else if (obj.chartFormat != 'candlestick') {
                            graphConfig.valueField = fname
                        }

                        if (obj.chartType == 'line') {
                            graphConfig.lineThickness = 2;

                            if (obj.chartFormat == 'smoothed line') {
                                graphConfig.type = "smoothedLine";
                            }

                            if (obj.chartFormat == 'step line') {
                                graphConfig.type = 'step';
                            }
                            else if (obj.chartFormat == 'step no risers') {
                                graphConfig.type = 'step';
                                graphConfig.noStepRisers = true;
                            } else {
                                graphConfig.bullet = bulletStyles[idx % bulletStyles.length];
                            }
                        }
                        else if ((obj.chartFormat == 'column and line' || obj.chartFormat == 'bar and line') && idx == 1) {
                            graphConfig.lineThickness = 2;
                            graphConfig.bullet = "round";
                        }
                        else if ((obj.chartType == 'area')) {
                            if ((obj.chartFormat == 'stacked area') || (obj.chartFormat == '100% stacked area')) {
                                graphConfig.fillAlphas = 0.75;
                            } else {
                                graphConfig.fillAlphas = Math.min(Math.max(1 / vfs.length, 0.15), 0.75);
                            }

                            graphConfig.lineAlpha = 0;
                        }
                        else if (obj.chartFormat == 'candlestick') {
                            graphConfig.balloonText = "10% percentile:<b>[[low]]</b><br>25% percentile:<b>[[open]]</b><br>75% percentile:<b>[[close]]</b><br>90% percentile:<b>[[high]]</b><br>";
                            graphConfig.closeField = fname + '.PERCENTILE_CONT_75';
                            graphConfig.fillAlphas = 0.9;
                            graphConfig.fillColors = "#7f8da9";
                            graphConfig.highField = fname + '.PERCENTILE_CONT_90';
                            graphConfig.lineColor = "#7f8da9";
                            graphConfig.lowField = fname + '.PERCENTILE_CONT_10';
                            graphConfig.negativeFillColors = "#db4c3c";
                            graphConfig.negativeLineColor = "#db4c3c";
                            graphConfig.openField = fname + '.PERCENTILE_CONT_25';
                            graphConfig.type = "candlestick";
                            graphConfig.valueField = fname + '.PERCENTILE_CONT_75'
                        }
                        else {
                            graphConfig.type = "column";
                            graphConfig.fillAlphas = 1;
                        }

                        if (obj.chartFormat == 'floating columns' || obj.chartFormat == 'floating bars') {
                            if (idx == 1) {
                                that.chart.graphs.push(graphConfig);
                            }
                        } else {
                            that.chart.graphs.push(graphConfig);
                        }

                        if (idx < valueAxes.length) {
                            var valueAxe = valueAxes[idx];

                            if (obj.chartFormat == 'logarithmic scale') {
                                valueAxe.logarithmic = true;
                            }

                            valueAxe.stackType = 'none';
                            if (obj.chartFormat == 'stacked' || obj.chartFormat == '3d stacked' || obj.chartFormat == 'stacked area' || obj.chartFormat == 'clustered and stacked' || obj.chartFormat == 'floating columns' && obj.chartFormat != 'floating bars') {
                                valueAxe.stackType = 'regular';
                            } else if (obj.chartFormat == '100% stacked' || obj.chartFormat == '3d 100% stacked' || obj.chartFormat == '100% stacked area' || obj.chartFormat == '100% stacked line') {
                                valueAxe.stackType = '100%'
                            }

                            /* On stacked graphs we need a single value axis */
                            if ((idx > 0) && (valueAxe.stackType != 'none')) {
                                if (valueAxes[idx].title != valueAxes[0].title) {
                                    valueAxes[0].title = ''
                                }
                                valueAxes[idx] = null;
                            }
                        }
                    } else if (obj.chartType == 'pie & donut') {
                        that.chart.valueField = fname;
                    } else if (obj.chartFormat == 'radar' || obj.chartFormat == 'polar') {
                        that.chart.graphs.push({
                            "balloonText": "<b>[[value]]</b>" + number_of_projects_info,
                            "bullet": bulletStyles[idx % bulletStyles.length],
                            "id": "AmGraph-" + idx,
                            "valueField": fname
                        });

                        var valueAxe = {
                            "axisTitleOffset": 20,
                            "id": "ValueAxis-1",
                            "minimum": 0,
                            "axisAlpha": 0.15,
                            "dashLength": 3
                        };
                        if (obj.chartFormat == 'polar') {
                            valueAxe.gridType = "circles";
                        }
                        that.chart.valueAxes = [valueAxe]
                    }
                });

                /* Only keep necessary value axes */
                if (!(obj.chartFormat == 'radar' || obj.chartFormat == 'polar')) {
                    this.chart.valueAxes = [];
                    $.each(valueAxes, function (idx, valueAxe) {
                        if (valueAxe != null) {
                            that.chart.valueAxes.push(valueAxe);
                        }
                    });
                }
            }
        },

        updateChartInfo: function (result) {
            // number of projects
            $('.totalobservations').text(result.info.number_of_projects);
            $('#total-project-counter').text(result.info.total_projects);

            if (result.info.number_of_projects == 0) {
                $('#no-data-message').show();
            } else {
                $('#no-data-message').hide();
            }
        },

        generateQueryDoc: function() {
            var info = this._getChartInfo();

            var result = {
                from: [],
                distinct: false,
                offset: 0,
                "limit": 100,
                "orderings": []
            };

            // for each variable
            $.each(info.values, function(idx, value) {
                var _from = {
                    type: value.type,
                    name: value.name + '_' + String(idx),
                    select: []
                };

                // push main value
                _from.select.push({
                   type: 'VALUE',
                   name: 'i' + String(idx) + '_' + value.name,
                   title: value.name,
                   aggregate: value.aggregate,
                   groupBy: false,
                   exclude: false
                });

                // push dimensions
                $.each($('select[name="category"] > option[data-forvariable="' + value.type + '"]'), function(jdx, opt) {
                    var name = $(opt).attr('value');

                    var dimension = {
                        type: $(opt).data('type'),
                        name: 'i' + String(idx) + '_' + name,
                        title: $(opt).text(),
                        groupBy: $(opt).attr('value') === $('select[name="category"]').val(),
                        exclude: true
                    };

                    // check if joined
                    if (idx > 0) {
                        $.each(result.from[0].select, function(kdx, dim) {
                            var dimName = dim.name.split('_').slice(1).join('_');

                            if (
                                (dimName === name) ||
                                (
                                    (['lat', 'lon'].indexOf(name.substr(0, 3)) >= 0) &&
                                    (dimName.substr(0, 3) === name.substr(0, 3))
                                )
                            ) {
                                dimension.joined = dim.name;
                                return false;
                            }
                        })
                    }
                    _from.select.push(dimension)
                });

                // add to query
                result.from.push(_from);
            });

            return result;
        },

        /* Gets the data based on the fields & options selected by the user */
        fetchChartData: function () {
            var obj = this.objects[this.current()];
            var that = this;

            // get category, values info & filters
            var ct = $('select[name="category"]').val();
            var info = this._getChartInfo();
            var filterStr = this.constructFiltersParam();
            filterStr = encodeURIComponent(filterStr);

            // request data
            $.ajax({
                url: '/queries/execute/',
                type: 'POST',
                data: {
                    query: JSON.stringify(this.generateQueryDoc()),
                    csrfmiddlewaretoken: $('[name="csrfmiddlewaretoken"]').val()
                },
                success: function (response) {
                    // create the required graphs
                    // todo update iframe

                    // update data table headers & data
                    var $table = $("#graph-data-table");
                    var colWidths = [];
                    var tableData = [[]];

                    $.each(response.headers.columns, function (idx, col) {
                        colWidths.push(250);
                        tableData[0][idx] = col.title
                    });

                    $.each(response.results, function (idx, res) {
                       tableData[idx + 1] = res;
                    });

                    $table.data('handsontable').updateSettings({
                        colWidths: colWidths
                    });

                    $table.handsontable("loadData", tableData);
                }
            })
        },

        tabMarker: {
            currentUnsaved: function () {
                var $active = $('#chart-picker li.active');
                if ($active.length == 0) {
                    return;
                }

                // check if already marked
                if ($active.find('.unsaved').length > 0) {
                    return
                }

                // mark as unsaved
                $active.find('a').append('<span class="unsaved">*</span>');
            },

            currentSaved: function () {
                $('#chart-picker li.active').find('.unsaved').remove();
            }
        },

        /* Switch to another chart */
        switchTo: function (idx) {
            // save previous options
            QueryToolbox.saveChartInfo();

            // change active tab
            $('#chart-picker li').removeClass('active');
            $('#chart-picker li:nth-of-type(' + (idx + 1) + ')').addClass('active');

            // switch chart
            var obj = this.objects[idx];
            this.renderChartOptions(obj);
            this.refreshValueFields();
            this.chart = obj.chart;
            this.chart.write('chartdiv');

            // update chart name field
            $('#chart-name input').val(obj.chartTitle);
        },

        /* Get the `CSRF` token */
        getCsrfMiddlewareToken: function () {
            return $('#chart-container input[name="csrfmiddlewaretoken"]').val()
        },

        setStatus: function (status, icon) {
            icon = icon || '';
            var extra = '';
            if (icon == 'loading') {
                extra = ' <i class="fa fa-spin fa-spinner"></i>'
            }
            else if (icon == 'check') {
                extra = ' <i class="fa fa-check"></i>'
            }

            $('#chart-status-msg').html(status + extra)
        },

        /* Save the current chart */
        save: function () {
            // get current chart (if any)
            var current = this.current();
            if (current < 0) {
                return;
            }

            // update status
            this.setStatus('Saving' + '...', 'loading');

            // save (in memory) the latest chart options
            this.saveChartInfo();

            // csrf token
            var data = {
                csrfmiddlewaretoken: this.getCsrfMiddlewareToken(),
                title: this.objects[current].chartTitle,
                chart_options: JSON.stringify(this.objects[current].chartOptions),
                chart_filters: this.objects[current].$chartFilters.html(),
                chart_type: this.objects[current].chartType,
                chart_format: this.objects[current].chartFormat
            };

            // add the chart ID if it's not a new chart
            if (typeof(this.objects[current].chartId) != 'undefined') {
                data.chart_id = this.objects[current].chartId;
            }

            // send the save request
            var that = this;
            $.ajax({
                url: '/chart/save/',
                type: 'POST',
                data: data,
                success: function (data) {
                    // save id & mark
                    that.objects[current].chartId = Number(data);
                    that.tabMarker.currentSaved();

                    // update status
                    that.setStatus('Saved', 'check');
                },
                error: function (xhr, status, error) {
                    console.log(error)
                }
            });
        },

        /* Load an existing chart */
        load: function (chartId) {
            var that = this;
            $.ajax({
                url: '/chart/open/' + chartId + '/',
                type: 'GET',
                success: function (data) {
                    that.addChart(data.chartOptions, data.chartFilters, data.chartPolicy, chartId, data.title)
                },
                error: function (xhr, status, error) {
                    console.log(error)
                }
            });
        },

        /* Close an open chart */
        close: function (chartIndex) {
            // get the tab that will be closed
            var $tab = $('#chart-picker li:nth-of-type(' + (chartIndex + 1) + ')');

            if ($tab.hasClass('active')) {
                // active tab closes - must switch to another tab
                var $newActive = $tab.prevAll(':not(.hidden)').first();
                if ($newActive.length == 0) {
                    $newActive = $tab.nextAll(':not(.hidden)').first();
                }
                if ($newActive.length > 0) {
                    this.switchTo($newActive.index())
                    $tab.addClass('hidden')
                }
            } else {
                // inactive tab closes
                $tab.addClass('hidden')
            }
        },

        rename: function (title) {
            var current = this.current();
            if (current < 0) {
                return
            }

            this.objects[current].chartTitle = title;
            $('#chart-picker li.active a .chartTitle').text(title);

            if (typeof(this.chart) != 'undefined') {
                this.chart.titles[0].text = title;
                this.chart.write('chartdiv');
            }

            this.tabMarker.currentUnsaved();
        },

        chartLoadDialog: {

            /* Show chart open modal */
            open: function () {
                var $modal = $('#chart-modal');

                // set title & content as loading
                $modal.find('.modal-title').text('Open an existing chart');
                var $modalBody = $modal.find('.modal-body');
                $modalBody.html('<i class="fa fa-spin fa-spinner fa-4x"></i>');

                // show the modal & autcscroll
                $('#chart-modal').dialog({
                    title: 'Select a query to open',
                    width: '50vw'
                });

                // get the user's charts
                $.ajax({
                    url: '/queries/simplified/list/',
                    type: 'GET',
                    success: function (data) {
                        $modalBody.html(data);

                        // apply Data Tables
                        $modalBody.find('table').DataTable({
                            bLengthChange: false,
                            language: {
                                emptyTable: 'No queries available',
                                zeroRecords: 'No queries found'
                            }
                        });
                    },
                    error: function (xhr, status, error) {
                        console.log(error)
                    }
                });
            },

            /* Close chart modal */
            close: function () {
                $('#chart-modal').dialog('close');
            }
        },

        /* Remove a value field */
        removeValue: function ($fieldset) {
            // update metric counters
            var $nxt = $fieldset,
                cnt = Number($fieldset.find('.metric-cnt').text()),
                xy = $fieldset.hasClass('xy');

            // in case of xy, we have to start from the correct fieldset & remove all three
            if (xy) {
                // account for group by fieldset
                if ($fieldset.index() % 3 != 1) {
                    return this.removeValue($($($fieldset).parent().fieldset().get(Math.floor($fieldset.index() / 3) * 3 + 1)));
                }
            }

            while ($nxt.next().length) {
                $nxt = $nxt.next();
                var cntVal = cnt;
                if (xy) {
                    cntVal = Math.floor((cnt - 1) / 3) * 3 - 1
                }
                $nxt.find('.metric-cnt').text(cntVal);
                cnt++;
            }

            // remove the field(s)
            if (xy) {
                $fieldset.next().next().remove();
                $fieldset.next().remove();
            }

            $fieldset.remove();
        },

        /* Responsible for editing queryset filters */
        filterManager: {
            /* Loads the appropriate information inside the popup */
            load: function () {
                // find active chart
                var current = QueryToolbox.current();
                if (current < 0) {
                    return;
                }

                var obj = QueryToolbox.objects[current];
                var filters = QueryToolbox.getFilterArray();

                // get the modal
                var $filterModal = $('#filters-modal');

                // set modal title
                $filterModal.find('.chart-title').text(obj.chartTitle);

                // show/hide expression settings
                var $filterExprSettings = $filterModal.find('#filter-expr-settings');
                if (filters.length > 1) {
                    $filterExprSettings.show();
                } else {
                    $filterExprSettings.hide();
                }

                // show filters
                var $filterTable = $filterModal.find('table');
                var $filterTableBody = $filterTable.find('tbody');
                $filterTableBody.empty();
                if (filters.length == 0) {
                    var $placeholderRow = $('<tr class="placeholder-row"><td>-</td><td><em>' + 'No filters found' + '</em></td><td></td></tr>');
                    $filterTableBody.append($placeholderRow);
                } else {
                    $.each(filters, function (idx, filter) {
                        var $filterTr = $('<tr><td>' + filter.name + '</td><td>' + filter.title + '</td><td><div class="remove-filter-btn"><i class="fa fa-times"></i></div></td></tr>');
                        $filterTableBody.append($filterTr);
                    })
                }

                // update filter counter
                this.updateFilterCounter();

                // filter join mode
                var $filterExpr = $('#chart-filters > .filter-expr');
                if ($filterExpr.length == 0) {
                    $('#chart-filters').append('<div class="filter-expr" data-expr_type="ALL_AND" />')
                } else {
                    var $filtersExprType = $('#filters-expr-type');
                    if ($filtersExprType.val() != $filterExpr.data('expr_type')) {
                        $filtersExprType.val($filterExpr.data('expr_type')).trigger("change")
                    }
                }
            },

            /* Open the filter manager popup */
            show: function () {
                // first load all info
                this.load();

                // show the modal
                $('#filters-modal').dialog({
                    title: 'Define query filters',
                    width: '70vw'
                });
            },

            getFilterOptions: function () {
                var chosenFilter = $('#new-filter-variable').val();
                var $inputContainer = $('#new-filter-value-container');
                $inputContainer.empty();

                // get options, comparison type & input type from the backend
                $.ajax({
                    url: '/chart/filter-info/?variable=' + chosenFilter,
                    type: 'GET',
                    success: function (data) {
                        var $input,
                            $filterOperand = $('#new-filter-operator'),
                            opSelector = 'option[value="<"], option[value="<="], option[value=">"], option[value=">="]';

                        if (data.type == 'number') {
                            $input = $('<input type="number" name="new-filter-value" />');

                            // update operands
                            $filterOperand.find(opSelector).removeAttr('disabled');
                            $filterOperand.select2()
                        }
                        else if (data.type == 'select') {
                            $input = $('<select name="new-filter-value" />');
                            $.each(data.options, function (idx, option) {
                                $input.append('<option value="\'' + option.value + '\'"">' + option.name + '</option>');
                            });

                            // update operands
                            $filterOperand.find(opSelector).attr('disabled', 'disabled');
                            $filterOperand.select2()
                        }

                        $inputContainer.append($input);
                        if (data.type == 'select') {
                            $input.select2();
                        }
                    },
                    error: function (xhr, status, error) {
                        console.log(error)
                    }
                });
            },

            addFilter: function (filterVariable, filterOperator, filterValue) {
                // add the new filters
                var filterVariable = filterVariable || $('#new-filter-variable').val();
                var filterOperator = filterOperator || $('#new-filter-operator').val();
                var filterValue = filterValue || $('[name="new-filter-value"]').val();
                var title = filterValue;
                if ($('select[name="new-filter-value"]').length > 0) {
                    title = $('select[name="new-filter-value"] option:selected').text()
                } else {
                    title = filterValue.split("'").join('')
                }
                var filterStr = filterVariable + filterOperator + filterValue;

                // humanized title of the filter
                var filterTitle = $('#new-filter-variable option[value="' + filterVariable + '"]').text() + filterOperator + title;

                // create filter name
                var filterName = 'F' + ($('#chart-filters .filter').length + 1);

                // add to filters
                $('#chart-filters').append('<div class="filter" data-name="' + filterName + '" data-title="' + filterTitle + '">' + filterStr + '</div>');

                // update counter
                this.updateFilterCounter();

                // re-load popup
                this.load();

                // mark as unsaved
                QueryToolbox.tabMarker.currentUnsaved()
            },

            getVariableFilters: function (variable) {
                var result = [];

                // find all filters for this variable
                $.each($('#chart-filters > .filter'), function (idx, filter) {
                    var $filter = $(filter);

                    if ($filter.text().indexOf(variable) == 0) {
                        result.push($filter.data('name'))
                    }
                });

                return result
            },

            setFilter: function (variable, value) {
                var filterClear = variable == 'istheinvestmentinabuilding_12' && value == '__clear__';

                // remove all filters for this variable
                var that = this;
                $.each(this.getVariableFilters(variable), function (idx, filterName) {
                    that.removeFilter(filterName, false)
                });

                // set new filter if any
                if (!filterClear) {
                    this.addFilter(variable, '=', value)
                } else {
                    this.load();
                }
            },

            removeFilter: function (filterName, reload) {
                reload = reload || true;

                // remove the filter
                $('#chart-filters > .filter[data-name="' + filterName + '"]').remove();

                // re-load popup
                if (reload) {
                    this.load();
                }

                // mark as unsaved
                QueryToolbox.tabMarker.currentUnsaved()
            },

            setExpressionType: function (expressionType) {
                // update expression type
                var $filterExpr = $('#chart-filters > .filter-expr');
                $filterExpr.data('expr_type', expressionType);
                $filterExpr.attr('data-expr_type', expressionType);

                // show/hide advanced expression input
                $expressionInput = $('#filters-expr-input');
                if (expressionType == 'CUSTOM') {
                    $expressionInput.show();
                } else {
                    $expressionInput.hide();
                }
            },

            updateFilterCounter: function () {
                var len = $('#chart-filters').find('> .filter').length;
                if (len == 0) {
                    len = '-'
                }
                $('.filter-edit-open > .filter-counter').text(len)
            }
        }

    };

    /* Filter dialog should always use select2 */
    $('#filters-modal select').select2();

    /* Add a new query */
    $('#add-chart').on('click', function () {
        QueryToolbox.addChart()
    });

    /* Reload chart data */
    $('body').on('click', '.fetch-graph-data', function () {
        QueryToolbox.fetchChartData()
    });

    /* Add a value field */
    $('body').on('click', '.add-value-field', function () {
        var $last = $('.chart-control .fieldset:last');

        if (!$last.hasClass('xy')) { // default case
            // clone last
            var $newField = $last.clone();

            // remove select2 & update counter
            $newField.find('.select2-container').remove();
            $newField.find('.metric-cnt').html($('.chart-control .fieldset').length);
            $newField.find('select').select2();

            // add delete button
            if ($newField.find('.col-suffix .value-remove-btn').length === 0) {
                $newField.find('.col-suffix').append('<div class="value-remove-btn" title="Remove value"><i class="fa fa-trash" /></div>');
            }

            // add
            $newField.insertAfter($last)
        } else { // xy case
            var $valField = $last;
            var $yField = $last.prev();
            var $xField = $yField.prev();

            // clone three last
            var $newValField = $valField.clone();
            var $newYField = $yField.clone();
            var $newXField = $xField.clone();

            var cnt = ($('.chart-control .fieldset').length - 1) / 3 + 1;
            $.each([$newValField, $newYField, $newXField], function (idx, $newField) {
                // remove select2 & update counter
                $newField.find('.select2-container').remove();
                $newField.find('.metric-cnt').html(cnt);
                $newField.find('select').select2();

                // add delete button
                if ($newField.find('.col-xs-3 .value-remove-btn').length === 0) {
                    $newField.find('.col-xs-3').append('<div class="value-remove-btn" title="Remove value"><i class="fa fa-trash" /></div>');
                }
            });

            // add all
            $newXField.insertAfter($last);
            $newYField.insertAfter($newXField);
            $newValField.insertAfter($newYField);
        }

        // mark as unsaved
        QueryToolbox.tabMarker.currentUnsaved();

        // redraw
        QueryToolbox.fetchChartData();
    });

    /* Initialize data table */
    $("#graph-data-table").handsontable({
        readOnly: true,
        colHeaders: true,
        rowHeaders: true
    });

    /* Switch chart */
    $('body').on('click', '#chart-picker li a', function (e) {
        QueryToolbox.switchTo($(this).parent().index());

        e.preventDefault();
        e.stopPropagation()
    });

    /* Close tab */
    $('body').on('click', '#chart-picker li a .close-tab', function (e) {
        QueryToolbox.close($(this).closest('li').index());

        e.preventDefault();
        e.stopPropagation()
    });

    /* On chart save */
    $('body').on('click', '#chart-save', function () {
        QueryToolbox.save();
    });

    /* On chart open dialog */
    $('body').on('click', '#chart-open', function () {
        QueryToolbox.chartLoadDialog.open();
    });

    /* On chart open */
    $('body').on('click', '.chart-open-teaser', function () {
        QueryToolbox.chartLoadDialog.close();
        QueryToolbox.load($(this).data('chart_id'));
    });

    /* On config field click */
    $('body').on('click', '.chart-control .value-options-btn', function () {
        QueryToolbox.optionManager.show($(this).closest('.fieldset').find('select'))
    });

    /* On value field change */
    $('body').on('change', 'select[name="value_field"], select[name="category"]', function (e) {

        // mark as unsaved
        QueryToolbox.tabMarker.currentUnsaved();

        // redraw
        QueryToolbox.fetchChartData();
    });

    /* On aggregate change */
    $('body').on('change', 'select[name="field_aggregate"]', function () {
        var $select = $(this).closest('.fieldset').find('select[name="value_field"]');

        $select.attr('data-aggregate', $(this).val());
        $select.data('aggregate', $(this).val());

        // mark as unsaved
        QueryToolbox.tabMarker.currentUnsaved();

        // redraw
        QueryToolbox.fetchChartData();
    });

    /* On chart rename */
    $('body').on('keyup', '#chart-name input', function () {
        QueryToolbox.rename($(this).val());
    });

    /* On chart edit filters */
    $('body').on('click', '.filter-edit-open', function () {
        QueryToolbox.filterManager.show();
    });

    /* On chart new filter variable change */
    $('body').on('change', '#new-filter-variable', function () {
        QueryToolbox.filterManager.getFilterOptions();
    });

    /* On chart add new filter */
    $('body').on('click', '.add-new-filter', function () {
        QueryToolbox.filterManager.addFilter();

        // redraw
        QueryToolbox.fetchChartData();
    });

    /* On filter expression type change */
    $('body').on('change', '#filters-expr-type', function () {
        // mark as unsaved
        QueryToolbox.tabMarker.currentUnsaved();

        QueryToolbox.filterManager.setExpressionType($(this).val());

        // redraw
        QueryToolbox.fetchChartData();
    });

    /* On value remove */
    $('body').on('click', '.value-remove-btn', function () {
        // mark as unsaved
        QueryToolbox.tabMarker.currentUnsaved();

        QueryToolbox.removeValue($(this).closest('.fieldset'));

        // redraw
        QueryToolbox.fetchChartData();
    });

    /* On filter remove */
    $('body').on('click', '.remove-filter-btn', function () {
        // mark as unsaved
        QueryToolbox.tabMarker.currentUnsaved();

        QueryToolbox.filterManager.removeFilter($(this).closest('tr').find('> td:first-of-type').text());

        // redraw
        QueryToolbox.fetchChartData();
    });

    /* On project type special filter change */
    $('body').on('click', '#chart-sidebar .project-type-option:not(.active)', function () {
        var value = $(this).data('value');

        // update the filter
        QueryToolbox.filterManager.setFilter('istheinvestmentinabuilding_12', value);

        // redraw
        QueryToolbox.fetchChartData();

        // update the UI
        $('#chart-sidebar .project-type-option').removeClass('active');
        $(this).addClass('active')
    });

    /* On formula editor popup open */
    $('body').on('click', '.formula-editor-open', function () {
        var $modal = $('#formulas-modal');

        // set title, hide save button & mark content as loading
        $modal.find('.modal-title').text('Manage custom formulas');
        var $modalBody = $modal.find('.modal-body');
        $modalBody.html('<div class="text-center" style="padding: 40px 0;"><i class="fa fa-spin fa-spinner fa-4x"></i></div>');
        var $closeBtn = $modal.find('.modal-footer button');
        $closeBtn.html('<i class="fa fa-save"></i> Save changes').hide();

        // show the modal & auto-scroll
        $modal.dialog();

        // get the user's charts
        $.ajax({
            url: '/formulas/',
            type: 'GET',
            success: function (data) {
                // insert formula editor & initialize
                $modalBody.html(data);
                onFormulaLoad();

                // show save button
                $closeBtn.show();
            },
            error: function (xhr, status, error) {
                console.log(error)
            }
        });
    });

    /* On formula editor popup save */
    $('body').on('click', '#formulas-modal .modal-footer .btn-default', function () {
        QueryToolbox.refreshValueFields()
    });

    /* Hotkeys */
    document.addEventListener("keydown", function (e) {
        if (e.keyCode == 83 && e.ctrlKey) { //Ctrl+S key pressed
            QueryToolbox.save();

            e.preventDefault();
            e.stopPropagation();
        }
        else if (e.keyCode == 79 && e.ctrlKey) { //Ctrl+O key pressed
            QueryToolbox.chartLoadDialog.open();

            e.preventDefault();
            e.stopPropagation();
        }
        else if (e.keyCode == 78 && e.ctrlKey) { //Ctrl+N key pressed
            // Will not work on Chrome (does not allow to override Ctrl+N)
            $('#select-chart-type').dialog();

            e.preventDefault();
            e.stopPropagation();
        }
    }, false);

    // export
    window.QueryToolbox = QueryToolbox;
});