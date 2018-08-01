/**
 * This method translates the custom expression given by the user to the correct JSON
 * @param customExpressionMap : this is a hashmap which has as key the symbol of the expression the user gave (e.g F1) and as value the value of the expression
 * @param expression : this is the expression given by the user
 * //TODO this is not working properly for parentheses (it ignores them). For example (F1 or F3) and F2 is evaluated as F1 or F3 and F2
 */
function buildCustomFilterFromExpressionMapAndExpression(customExpressionMap, expression) {
    var filterTree = {};
    var clearExpression = expression.replace("(", "").replace(")", "");
    var expressionAndOperationTable = clearExpression.split(" ");
    var expressionTable = expressionAndOperationTable.filter(expr => expr.startsWith("F"));
    var operatorTable = expressionAndOperationTable.filter(expr => !expr.startsWith("F"));
    var j = 0;
    for (var i = 0; i < expressionTable.length; i++) {
        var newFilter = customExpressionMap[expressionTable[i]];
        if (i === 0) {
            filterTree = newFilter;
        } else {
            filterTree = {
                a: newFilter,
                op: operatorTable[j],
                b: JSON.parse(JSON.stringify(filterTree))
            };
            j++;
        }
    }
    return filterTree;
}

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

            var chartTitle = chartTitle || 'Query ' + ($('#chart-picker li').length + 1);

            // this.chart = $('<iframe />');

            // save
            var obj = {
                'chartId': chartId,
                'tempChartId': chartId,
                'chartTitle': chartTitle
            };
            this.objects.push(obj);

            // add tab
            $('#chart-picker').find('li').removeClass('active');
            $('#chart-picker').append('<li class="active"><a href="#"><span class="chartTitle">' + chartTitle + '</span> <i class="fa fa-times close-tab"></i></a></li>');

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
            // $('#chartdiv')
            //     .empty()
            //     .append(this.chart);
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
                            metric: '' // chartPolicy.categories[0].value
                        },
                        fields: []
                    };

                    /* for (var j = 0; j < chartPolicy.incrStep; j++) {
                        chartOptions.fields.push({
                            metric: chartPolicy.valueFields[0].value
                        })
                    } */

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
                url: '/queries/simplified/config/',
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
            var $fieldSelect = $('<select />')
                .attr('name', config.name);

            if (config.name === 'category') {
                $fieldSelect.attr('multiple', 'multiple');
            }
            if (config.name === 'orderby') {
                $fieldSelect.attr('multiple', 'multiple');
            }

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
                $fieldSelect.append('<option value="">No value</option>');
            }
            var $fieldInputShown;
            $.each(config.choices, function (idx, choice) {
                var $option = $('<option />');
                if(config.value === choice.value) { // john's addition to have only the selected variable as option
                    $option.attr('value', choice.value);
                    $option.text(choice.title + ' (' + config.unit + ')');
                    if (typeof(choice.type) !== 'undefined') {
                        $option.data('type', choice.type);
                        $option.attr('data-type', choice.type);
                    }
                    if (typeof(choice.forVariable) !== 'undefined') {
                        $option.data('forvariable', choice.forVariable);
                        $option.attr('data-forvariable', choice.forVariable);
                    }

                    $fieldSelect.append($option);

                    // $fieldSelect.replaceWith($('<input class="form-control"  style="width: 100%; height: 100%;" value="'+$fieldSelect.val()+'"/>'));
                    $fieldInputShown = $('<input class="form-control" readonly style="width: 100%; height: 100%;"/>')
                    if (typeof(config.aggregate) !== 'undefined') {
                        $fieldInputShown.attr('data-aggregate', config.aggregate);
                        $fieldInputShown.data('aggregate', config.aggregate);
                    }
                    $fieldInputShown.attr('data-type', $option.attr('data-type'));
                    $fieldInputShown.attr('data-forvariable', $option.attr('data-forvariable'));
                    $fieldInputShown.val(choice.title + ' (' + config.unit + ')');

                    var $fieldInput = $('<input class="hidden" style="width: 100%; height: 100%;"/>').attr('name', config.name);
                    if (config.id) {
                        $fieldInput.attr('id', config.id);
                    }
                    if (typeof(config.aggregate) !== 'undefined') {
                        $fieldInput.attr('data-aggregate', config.aggregate);
                        $fieldInput.data('aggregate', config.aggregate);
                    }
                    $fieldInput.attr('data-type', $option.attr('data-type'));
                    $fieldInput.attr('data-forvariable', $option.attr('data-forvariable'));

                    $fieldSelect = $fieldInput;
                }
            });

            var inlineLabel = '';
            if (config.name === 'category') {
                inlineLabel = config.label;
            }
            if (config.name === 'orderby') {
                inlineLabel = config.label;
            }

            // set field value
            $fieldSelect.val(config.value);
            var $fieldset = $('<div class="fieldset">' + (inlineLabel ? '' : config.label + '<br />') + '<div class="row" style="margin: 0"><div class="col-xs-3 col-prefix" style="' + (inlineLabel ? 'padding: 0' : '') +'">' + inlineLabel + '</div><div class="col-xs-8 col-main"></div><div class="col-xs-1 col-suffix"></div></div></div>');
            $fieldset.find('.col-main').append($fieldSelect);
            $fieldset.find('.col-main').append($fieldInputShown);

            if (config.xy) {
                $fieldset.addClass('xy')
            }

             if (typeof(config.aggregate) !== 'undefined') {
                $fieldset.find('.col-prefix').append($aggregateSelect);
            }

            if (config.canDelete) {
                $fieldset.find('.col-suffix').append('<div class="value-remove-btn" title="Remove value"><i class="fa fa-trash" /></div>')
            }

            $dimensionsDiv = $('<div class="collapse"> <ul></ul></div>');
            $ul = $dimensionsDiv.find('ul');

            for(var i in config.dimensions){
                $li = $('<li>'+config.dimensions[i].title+'</li>');
                $ul.append($li);
            }
            $fieldset.find('.col-main').append($dimensionsDiv);

            return $fieldset;
        },

        /* renders the chart options & filters UI components */
        renderChartOptions: function (obj) {
            var $controlList = $('#chart-control-list');
            var $chartControls = $('<div class="chart-control" />');
            var defaultAggregate = obj.chartPolicy.defaultAggregate;

            /* empty from previous controls */
            $controlList.empty();

            // add add filter & draw buttons
            var $btnContainer = $('<div class="row btn-container">').css('padding', '0').css('margin-left', '0');
            if (obj.chartOptions.fields.length + 1 < obj.chartPolicy.max) {
                $btnContainer.append('<div class="add-value-field btn btn-default btn-sm pull-left bg-color--blue" style=""><i class="fa fa-plus"></i> Select data</div>')
            }

            $btnContainer.append('<div class="btn btn-sm btn-primary pull-right fetch-graph-data hidden"><i class="fa fa-line-chart"></i> Draw</div>');
            $btnContainer.append('<div id="run-query-btn" class="btn btn-sm btn-default pull-right bg-color--blue after-data-selection" style="background: #a00000 !important;"><i class="fa fa-play-circle"></i> Run</div>');
            $controlList.append($btnContainer);


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


            // add group by and order by fields
            var $queryControlsContainer = $('<div class="row after-data-selection" id="query-controls-container">').css('padding', '0').css('margin-left', '0').css('margin-top', '20px');

            // create group select
            var $groupSelectContainer = this.renderChartOptionsField({
                choices: obj.chartPolicy.categories,
                name: 'category',
                id: 'id_category',
                label: 'Group by',
                value: obj.chartOptions.group.metric
            });
            $queryControlsContainer.append($groupSelectContainer);

            // create order select
            var $orderSelectContainer = this.renderChartOptionsField({
                choices: obj.chartPolicy.categories,
                name: 'orderby',
                id: 'id_orderby',
                label: 'Order by',
                value: obj.chartOptions.group.metric
            });
            $queryControlsContainer.append($orderSelectContainer);

            $controlList.append($queryControlsContainer);

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
                    'a': $flt.data('a'),
                    'op': $flt.data('op'),
                    'b': $flt.data('b')
                });
            });

            return filters
        },

        constructFiltersParam: function (queryDocument) {
            if (queryDocument === undefined) {
                return
            }

            // gather individual filters
            var filters = this.getFilterArray();
            var time_dim_id = $('#selected_dimensions option[data-type="time"]').val();
            if (startdate !== null) filters.push({a: time_dim_id, op: 'gte', b: startdate.toString()});
            if (enddate !== null) filters.push({a: time_dim_id, op: 'lte', b: enddate.toString()});

            var filterTree = {};

            var expression = $('#filters-expr-input').val();
            var exprType = $('#chart-filters > .filter-expr').attr('data-expr_type');
            var customExpressionMap = {};

            // if (filters.length === 0) {
            //     return filterTree;
            // }

            // find pattern
            // assume ALL_AND
            $.each(filters, function (idx, filter) {
                var aName;
                $.each(queryDocument.from, function (idx, _from) {
                    $.each(_from.select, function (jdx, attr) {
                        if (attr.type === "VALUE") {
                            // if (String(attr.name).split(new RegExp("i[0-9]+_"))[1] === filter.a) {
                            if (parseInt(_from.type) === parseInt(filter.a)) {
                                aName = attr.name;
                            }
                        }
                        else {
                            if (attr.type == filter.a) {
                                aName = attr.name;
                            }
                        }
                    })
                });
                var newFilter = {
                    a: aName,
                    op: filter.op,
                    b: typeof(filter.b) === 'string' ? "'" + filter.b + "'" : filter.b
                };
                if (exprType === 'CUSTOM') {
                    var mapIndex = idx + 1;
                    customExpressionMap["F" + mapIndex] = newFilter;
                } else {
                    if (idx === 0) {
                        filterTree = newFilter;
                    } else {
                        var exprOperator = (exprType === 'ALL_OR') ? 'OR' : 'AND';
                        filterTree = {
                            a: newFilter,
                            op: exprOperator,
                            b: JSON.parse(JSON.stringify(filterTree))
                        };
                    }
                }
            });

            if (exprType === 'CUSTOM') {
                filterTree = buildCustomFilterFromExpressionMapAndExpression(customExpressionMap,expression);
            }
            var latitude_dim_id = $('#selected_dimensions option[data-type="latitude"]').val();
            var longitude_dim_id = $('#selected_dimensions option[data-type="longitude"]').val();
            if ((bounds[0] !== -90) || (bounds[2] !== 90) || (bounds[1] !== -180) || (bounds[3] !== 180)){
                // filters.push({a: '<'+latitude_dim_id+','+longitude_dim_id+'>', op: 'inside_rect', b: '<<'+bounds[0].toString()+','+bounds[1].toString()+'>,<'+bounds[2].toString()+','+bounds[3].toString()+'>>'});
                var newFilter = {
                    a: '<'+latitude_dim_id+','+longitude_dim_id+'>',
                    op: 'inside_rect',
                    b: '<<'+bounds[0].toString()+','+bounds[1].toString()+'>,<'+bounds[2].toString()+','+bounds[3].toString()+'>>'
                };
                if (Object.keys(filterTree).length === 0){
                    filterTree = newFilter;
                }
                else{
                    filterTree = {
                        a: newFilter,
                        op: 'AND',
                        b: JSON.parse(JSON.stringify(filterTree))
                    };
                }
            }


            // console.log(filters);

            return filterTree;
        },

        _getChartInfo: function () {
            var values = [], columns = [];
            // var vfs = $('select[name="value_field"]');
            var vfs = $('input[name="value_field"]');

            $.each(vfs, function (idx, vf) {
                // create the field name (including the aggregate)
                // var aggregate = $(vf).data('aggregate');
                var aggregate = $(vf).closest('.row').find('*[name="field_aggregate"]').val();
                // if aggregate property was not found
                if (typeof(aggregate) === "undefined") {
                    aggregate = 'AVG'
                }

                var fname = $(vf).val();

                values.push({
                    name: fname,
                    // type: $(vf).find('option:selected').data('type'),
                    type: $(vf).attr('data-type'),
                    aggregate: aggregate
                });

                // field title
                var ttl_prefix = '';
                if (aggregate != '') {
                    ttl_prefix = $('select[name="field_aggregate"] option[value="' + aggregate + '"]').get(0).textContent + ' '
                }
                // var ttl = ttl_prefix + $(vf).find('option:selected').text();
                var ttl = ttl_prefix + $(vf).val();

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
            console.log(info);
            var result = {
                from: [],
                distinct: false,
                offset: 0,
                "limit": ($('#limit_container select').val() !== 'none')? parseInt($('#limit_container select').val()) : [],
                "orderings": []
            };

            // for each variable
            $.each(info.values, function(idx, value) {
                var _from = {
                    type: value.type,
                    name: String(value.name).split("_pk_")[1] + '_' + String(idx),
                    select: []
                };

                // push main value
                _from.select.push({
                   type: 'VALUE',
                   name: 'i' + String(idx) + '_' + String(value.name).split("_pk_")[1],
                   title: String(value.name).split("_pk_")[1],
                   aggregate: value.aggregate,
                   groupBy: false,
                   exclude: false
                });
                // alert(value.name);
                // push dimensions
                $.each($('#selected_dimensions > option[data-forvariable="' + value.name + '"]'), function(jdx, opt) {
                    // alert("Dimension" + $(opt).data('type'));
                    var name = $(opt).data('type');
                    var groupBy = $('select[name="category"]').val().indexOf(String($(opt).attr('value'))) >= 0;
                    var dimAggregate = '';
                    // var dimName = String($(opt).attr('value'));
                    if ((name.indexOf('latitude') >= 0) || (name.indexOf('longitude') >= 0)) {
                        // alert("Lat on Lon");
                        if ($("#spatial_resolution").val() !== "none"){
                            // alert("spatial_resolution is not None");
                            groupBy = true;
                            if ($("#spatial_resolution").val() === "1")
                                dimAggregate = 'round0';
                            else if($("#spatial_resolution").val() === "0.1")
                                dimAggregate = 'round1';
                            else if($("#spatial_resolution").val() === "0.01")
                                dimAggregate = 'round2';
                        }
                    }
                    if (name.indexOf('time') >= 0) {
                        // alert("Lat on Lon");
                        if ($("#temporal_resolution").val() !== "none"){
                            // alert("temporal_resolution is not None");
                            groupBy = true;
                            if ($("#temporal_resolution").val() === "minute")
                                dimAggregate = 'date_trunc_minute';
                            else if($("#temporal_resolution").val() === "hour")
                                dimAggregate = 'date_trunc_hour';
                            else if($("#temporal_resolution").val() === "day")
                                dimAggregate = 'date_trunc_day';
                            else if($("#temporal_resolution").val() === "month")
                                dimAggregate = 'date_trunc_month';
                            else if($("#temporal_resolution").val() === "year")
                                dimAggregate = 'date_trunc_year';

                            // alert(dimAggregate);

                        }
                    }

                    var orderBy = $('select[name="orderby"]').val().indexOf(String($(opt).attr('value'))) >= 0;

                    var dimension = {
                        type: $(opt).attr('value'),
                        name: 'i' + String(idx) + '_' + name,
                        title: $(opt).text(),
                        groupBy: groupBy,
                        aggregate: dimAggregate,
                        exclude: !groupBy && value.aggregate
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
                                dimension.exclude = true;
                                return false;
                            }
                        })
                    }
                    _from.select.push(dimension);
                    if(orderBy) {
                        var selected_index = $('select[name="orderby"]').val().indexOf(String($(opt).attr('value')));
                        var ordering = $('select[name="orderby"]').find('option:selected').eq(selected_index).data('ordering');
                        result.orderings.push({type: ordering, name: 'i' + String(idx) + '_' + name});
                    }
                });

                // add to query
                result.from.push(_from);

            });

            // add filters
            result.filters = this.constructFiltersParam(result);

            // add orderings


            return result;
        },

        /* Gets the data based on the fields & options selected by the user */
        fetchChartData: function () {},
        fetchQueryData: function () {
            var that = this;

            var obj = this.objects[this.current()];

            // update available filters
            this.filterManager.updateFilters(this._getChartInfo().values);

            var doc = this.generateQueryDoc();
            if (doc.from.length === 0) {
                return
            }
            if($('#limit_container select').val() !== 'none') {
                if (parseInt($('#limit_container select').val()) > 50) {
                    doc['limit'] = 50;
                    doc['offset'] = parseInt($('#offset_input').val());
                }
            }
            else{
                doc['limit'] = 50;
                doc['offset'] = parseInt($('#offset_input').val());
            }
            // get category, values info & filters
            var filterStr = this.constructFiltersParam();
            filterStr = encodeURIComponent(filterStr);

            // request data
            var runQuery = function(id) {
                // update data table headers & data
                var $table = $("#graph-data-table");
                $table.find('thead').empty();
                $table.find('tbody').empty();
                $.ajax({
                    url: '/queries/execute/',
                    type: 'POST',
                    data: {
                        query: JSON.stringify(doc),
                        csrfmiddlewaretoken: $('[name="csrfmiddlewaretoken"]').val()
                    },
                    success: function (response) {
                        $('.no-data-message').hide();
                        $('#chartdiv').show();
                        $('#paginationDiv').show();

                        // create the required graphs
                        // todo improve updating iframe
                        var y_var = doc.from[0].select[0].name;
                        var x_var = doc.from[0].select[1].name;
                        $.each(doc.from[0].select, function (idx, s) {
                            if (s.groupBy) {
                                x_var = s.name
                            }
                        });
                        var iframe = $('<iframe  onload="hide_gif();" />');
                        $("#viz_container iframe").remove();
                        $("#viz_container").append(iframe);
                        // $('#viz_container iframe').attr('src', '/visualizations/get_line_chart_am/?query=' + id + '&y_var[]=' + y_var + '&x_var=' + x_var);



                        var $header = $('<tr />');
                        $.each(response.headers.columns, function (idx, col) {
                            $header.append($('<td />').text(col.title))
                        });
                        $table.find('thead').append($header);

                        $.each(response.results, function (idx, res) {
                            var $row = $('<tr />');
                            $.each(res, function(jdx, resItem) {
                                $row.append($('<td />').text(resItem));
                            });

                            $table.find('tbody').append($row);
                        });
                        updatePaginationButtons();
                        $("#chart-content-tabs li").eq(1).find('a').click();
                        $("#chart-content-tabs li").eq(0).find('a').click();
                    },
                    error: function (response) {
                        hide_gif();
                        $('#chartdiv').hide();
                        $('#paginationDiv').hide();
                        $('.no-data-message').show();
                        alert('We are sorry, an error occurred.');
                    }
                })
            };

            // hack due to visualizations needing the query id
            // first save
            QueryToolbox.save(runQuery, 1);
        },

        tabMarker: {
            currentUnsaved: function () {
                var $active = $('#chart-picker li.active');
                if ($active.length === 0) {
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
            $('#chartdiv')
                // .empty()
                .append(this.chart);

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
            if (icon === 'loading') {
                extra = ' <i class="fa fa-spin fa-spinner"></i>'
            }
            else if (icon === 'check') {
                extra = ' <i class="fa fa-check"></i>'
            }
            else if (icon === 'failed') {
                extra = ' <i class="fa fa-exclamation-triangle"></i>'
            }

            $('#chart-status-msg').html(status + extra)
        },

        /* Save the current chart */
        save: function (callback, temp) {
            // get current chart (if any)
            var current = this.current();
            if (current < 0) {
                return;
            }

            // update status
            this.setStatus('Saving...', 'loading');

            // save (in memory) the latest chart options
            this.saveChartInfo();

            // csrf token
            var data = {
                csrfmiddlewaretoken: this.getCsrfMiddlewareToken(),
                document: JSON.stringify(this.generateQueryDoc()),
                title: this.objects[current].chartTitle,
                v2_fields: JSON.stringify(this.objects[current].chartOptions),
                v2_options: this.objects[current].$chartFilters.html()
            };

            // send the save request
            var that = this;
            var url;
            if (temp === 1){
                url = '/queries/save/' + (this.objects[current].tempChartId ? this.objects[current].tempChartId + '/' : '') + '1/'
            }
            else{
                url = '/queries/save/' + (this.objects[current].chartId ? this.objects[current].chartId + '/' : '') + '0/'
            }
            $.ajax({
                url: url,
                type: 'POST',
                data: data,
                success: function (data) {
                    // save id & mark
                    if (temp === 1){
                        that.objects[current].tempChartId = Number(data.pk);
                    }
                    else{
                        that.objects[current].chartId = Number(data.pk);
                    }
                    that.tabMarker.currentSaved();

                    // update status
                    that.setStatus('Saved', 'check');

                    $('#selected_query').val(parseInt(data.pk));
                    // run callback
                    if (callback) {
                        callback(data.pk)
                    }
                },
                error: function (xhr, status, error) {
                    that.setStatus('Saving failed.', 'failed');
                }
            });
        },

        /* Load an existing chart */
        load: function (chartId) {
            var that = this;
            $.ajax({
                url: '/queries/simplified/open/' + chartId + '/',
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
            var variable_type = $fieldset.find('input[name="value_field"]').attr("data-type");
            $('#selected_dimensions > option[data-forvariable^="' + variable_type + '_"]').remove();
            // $('#id_category > option[data-forvariable^="' + variable_type + '_"]').remove();
            // $('#id_orderby > option[data-forvariable^="' + variable_type + '_"]').remove();

            id_category
            $fieldset.remove();
            if(cnt===0){
                $('.after-data-selection').each(function () {
                    $(this).hide();
                });
                $('.chartdiv').hide();
                $('#paginationDiv').hide();
                var $table = $("#graph-data-table");
                $table.find('thead').empty();
                $table.find('tbody').empty();
            }
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

            updateFilters: function(variables) {
                var variableTypes = [];
                $.each(variables, function(idx, variable) {
                   variableTypes.push(variable.type);
                });

                // $.each($('#new-filter-variable').find('option'), function(idx, opt) {
                //     var $opt = $(opt);
                //
                //     if (
                //         (variableTypes.indexOf($opt.data('forvariabletype')) >= 0) ||
                //         (variableTypes.indexOf($opt.data('forvariable')) >= 0)
                //
                //     ) {
                //         $opt.removeAttr('disabled');
                //     } else {
                //         $opt.attr('disabled', 'disabled');
                //     }
                // });
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
                var filterType = $('#new-filter-variable option:selected').data('type');
                var $inputContainer = $('#new-filter-value-container');
                var $info = $('#new-filter-info-message');
                $inputContainer.empty();
                var url = '';
                if (filterType == 'variable'){
                    url = '/queries/simplified/filter-info/variable/' + chosenFilter + '/'
                }
                else{
                    url = '/queries/simplified/filter-info/dimension/' + chosenFilter + '/'
                }

                // get options, comparison type & input type from the backend
                $.ajax({
                    url: url,
                    type: 'GET',
                    success: function (data) {
                        var $input,
                            $filterOperand = $('#new-filter-operator'),
                            opSelector = 'option[value="<"], option[value="<="], option[value=">"], option[value=">="]';

                        if (data.options) {
                            $input = $('<select name="new-filter-value" />');
                            $.each(data.options, function (idx, option) {
                                var val = option.value;
                                if (typeof(val) === 'string') {
                                    val = "'" + val + "'";
                                }

                                $input.append('<option value="' + val + '">' + option.name + '</option>');
                            });

                            // update operands
                            $filterOperand.select2()
                        }

                        else if (data.type === 'number') {
                            $input = $('<input type="number" name="new-filter-value" />');
                        }
                        else {
                            $input = $('<input type="text" name="new-filter-value" />');
                        }

                        // enable/disable operators
                        if (data.orderable) {
                            $filterOperand.find(opSelector).removeAttr('disabled');
                        } else {
                            $filterOperand.find(opSelector).attr('disabled', 'disabled');
                        }
                        $filterOperand.select2();

                        $inputContainer.append($input);
                        if (data.options) {
                            $input.select2();
                        }

                        // show help message
                        var message = '';
                        if (data.orderable && (typeof(data.min) !== 'undefined')) {
                            message += 'Minimum value: ' + String(data.min)
                        }
                        if (data.orderable && (typeof(data.min) !== 'undefined')) {
                            message += 'Maximum value: ' + String(data.max)
                        }
                        $info.text(message);
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
                // type: variable or dimension
                var filterType = $('[name="new-filter-value"]').attr('data-type');
                var title = filterValue;
                if ($('select[name="new-filter-value"]').length > 0) {
                    title = $('select[name="new-filter-value"] option:selected').text()
                } else {
                    title = filterValue.split("'").join('')
                }
                var filterStr = filterVariable + filterOperator + filterValue;

                // humanized title of the filter
                var filterTitle = $('#new-filter-variable option[value="' + filterVariable + '"]').text() + ' ' +filterOperator + ' ' + title;

                // create filter name
                var filterName = 'F' + ($('#chart-filters .filter').length + 1);

                // add to filters
                $('#chart-filters').append('<div class="filter" data-name="' + filterName + '" data-title="' + filterTitle +
                    '" data-a="' + filterVariable +'" data-op="' + filterOperator + '" data-b="' + filterValue + '">' + filterStr + '</div>');

                // update counter
                this.updateFilterCounter();

                // re-load popup
                this.load();
                console.log( filterStr );
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

    $('#limit_container select').select2({tags: true});

    /* Add a new query */
    $('#add-chart').on('click', function () {
        // QueryToolbox.addChart()
        reset();
    });

    /* Reload chart data */
    $('body').on('click', '.fetch-graph-data', function () {
        QueryToolbox.fetchChartData()
    });

    /* Add a value field */
    $('body').on('click', '.add-value-field', function () {
        var $last = $('.chart-control .fieldset:last');

        $('#select-data-modal').dialog({
            width: '60vw',
            position: {my: 'center'},
            title: 'Select data'
        });

    });

    $('#selection-close-btn').on('click', function () {
        $('#select-data-modal').dialog('close');
    });

    /* Add a value field */
    $('#selection-confirm-btn').on('click', function() {
        var newField = window.getDataSelection();
        if (newField.value != ""){


            var $chartControls = $('#chart-control-list > .chart-control');
            var label = 'Metric #<span class="metric-cnt">' + ($chartControls.find('> *').length ) + '</span>';

            var obj = QueryToolbox.objects[QueryToolbox.current()];

            var $fieldset = QueryToolbox.renderChartOptionsField({
                choices: obj.chartPolicy.valueFields,
                emptyChoice: false,
                name: 'value_field',
                label: label,
                value: newField.value,
                unit: newField.unit,
                dimensions: newField.dimensions,
                aggregate: newField.aggregate,
                aggregates: obj.chartPolicy.aggregates,
                canConfig: true,
                canDelete: true,
                xy: false
            });

            var $category = $('[name="category"]');
            var $orderby = $('[name="orderby"]');
            var $dimensions = $('#selected_dimensions');
            var $filter_variables = $('#new-filter-variable');

            $.each(newField.dimensions, function (id, data) {
                if ($category.find("option[name='" + data.title + "']").length) {
                    // Create a DOM Option and pre-select by default
                    var newOption = new Option(data.title, data.value, false, false);
                    newOption.setAttribute('data-forVariable', newField.value);
                    newOption.setAttribute('data-type', data.title);
                    newOption.setAttribute('name', data.title);
                    // Append it to the select
                    // $category.append(newOption).trigger('change');
                    $dimensions.append(newOption);
                } else {
                    // Create a DOM Option and pre-select by default
                    var newOption = new Option(data.title, data.value, false, false);
                    newOption.setAttribute('data-forVariable', newField.value);
                    newOption.setAttribute('data-type', data.title);
                    newOption.setAttribute('name', data.title);
                    // Append it to the select
                    $category.append(newOption).trigger('change');

                    var newOption = new Option(data.title + ' - ASC', data.value, false, false);
                    newOption.setAttribute('data-forVariable', newField.value);
                    newOption.setAttribute('data-type', data.title);
                    newOption.setAttribute('data-ordering', 'ASC');
                    newOption.setAttribute('name', data.title);
                    // Append it to the select
                    $orderby.append(newOption).trigger('change');

                    var newOption = new Option(data.title + ' - DESC', data.value, false, false);
                    newOption.setAttribute('data-forVariable', newField.value);
                    newOption.setAttribute('data-type', data.title);
                    newOption.setAttribute('data-ordering', 'DESC');
                    newOption.setAttribute('name', data.title);
                    // Append it to the select
                    $orderby.append(newOption).trigger('change');

                    var newOption = new Option(data.title, data.value, false, false);
                    newOption.setAttribute('data-forVariable', newField.value);
                    newOption.setAttribute('data-type', data.title);
                    newOption.setAttribute('name', data.title);
                    $dimensions.append(newOption);

                    var newOption = new Option(data.title, data.value, false, false);
                    newOption.setAttribute('data-forVariable', newField.value);
                    newOption.setAttribute('data-type', data.title);
                    newOption.setAttribute('name', data.title);
                    $filter_variables.append(newOption);
                }
            });

            // add variables to filters too
            var newOption = new Option(newField.title, newField.id, false, false);
            newOption.setAttribute('data-forVariable', '');
            newOption.setAttribute('data-type', 'variable');
            newOption.setAttribute('name', newField.value);
            $filter_variables.append(newOption);

            QueryToolbox.filterManager.updateFilters(QueryToolbox._getChartInfo().values);

            var v = $category.val();
            $.each(newField.groupBy, function (idx, f) {
                v.push(f);
            });
            $category.val(v).trigger('change.select2');

            $fieldset.find('select').select2();

            $chartControls.append($fieldset);

            // show other query controls
            if($chartControls.find('> *').length>0) {
                $('.after-data-selection').each(function () {
                    $(this).show();
                });
            }

            // mark as unsaved
            QueryToolbox.tabMarker.currentUnsaved();

            // redraw
            QueryToolbox.fetchChartData();
        }

        // close popup
        // $('#select-data-modal').dialog('close');
        $(".variable-list .selected").removeClass("selected");
        $("#selection-aggregate").val(null).trigger('change');
        $("#group-by-select").val(null).trigger('change');

    });

    $('#select-data-modal').on('dialogclose', function(event) {
        $('.selection-confirm .col-xs-12').addClass('hidden');
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
        QueryToolbox.save(function (id) {}, 0);
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
    $('body').on('change', 'select[name="value_field"]', function (e) {

        // mark as unsaved
        QueryToolbox.tabMarker.currentUnsaved();

        // redraw
        QueryToolbox.fetchChartData();
    });

    /* On spatial resolution field change */
    $('body').on('change', '#spatial_resolution', function (e) {

        if($("#spatial_resolution").val() != "none"){
            $("select[name='field_aggregate']").each(function () {
                $(this).val("AVG");
                $(this).trigger("change");
            });

        }

        // mark as unsaved
        QueryToolbox.tabMarker.currentUnsaved();

        // redraw
        QueryToolbox.fetchChartData();
    });

    /* On temporal resolution field change */
    $('body').on('change', '#temporal_resolution', function (e) {

        if($("#temporal_resolution").val() != "none"){
            $("select[name='field_aggregate']").each(function () {
                $(this).val("AVG");
                $(this).trigger("change");
            });

        }

        // mark as unsaved
        QueryToolbox.tabMarker.currentUnsaved();

        // redraw
        QueryToolbox.fetchChartData();
    });

    /* On category field change */
    $('body').on('change', 'select[name="category"]', function (e) {

        if($("select[name='category']").val().length > 0){
            $("select[name='field_aggregate']").each(function () {
                $(this).val("AVG");
                $(this).trigger("change");
            });

        }
        // else{
        //     $("select[name='field_aggregate']").each(function () {
        //         $(this).val("");
        //         $(this).trigger("change");
        //     });
        // }

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
        $modal.dialog({
            title: 'Formula editor',
            width: '90vw',
            position: {at: 'center top'}
        });

        // get the user's charts
        $.ajax({
            url: '/queries/formulas/',
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

    /* On run query btn click, execute the query and fetch results */
    $('body').on('click', '#run-query-btn', function () {
        $(".outputLoadImg").hide();
        $(".outputLoadImg").delay(100).show();
    // $("#run-query-btn").click(function () {
        $('#offset_input').val(0);
        QueryToolbox.fetchQueryData();
    });

    /* On next page btn click, increase the offset and execute the query to fetch results */
    $('body').on('click', '#dataNextBtn', function () {
        $(".outputLoadImg").show();
        $('#offset_input').val(parseInt($('#offset_input').val())+50);
        QueryToolbox.fetchQueryData();
    });
    /* On prev page btn click, decrease the offset and execute the query to fetch results */
    $('body').on('click', '#dataPrevBtn', function () {
        $(".outputLoadImg").show();
        $('#offset_input').val(parseInt($('#offset_input').val())-50);
        QueryToolbox.fetchQueryData();
    });

    $('body').on('click', '.fieldset input[readonly]', function () {
        $(this).closest('.fieldset').find('.collapse').collapse("toggle");
        // $('.collapse').collapse() ;
    });

    function updatePaginationButtons() {
        if($("#graph-data-table tbody tr").length < 50){
            $('#dataNextBtn').prop('disabled', true);
        }
        else{
            $('#dataNextBtn').prop('disabled', false);
        }
        if(parseInt($('#offset_input').val()) <= 0){
            $('#offset_input').val(0);
            $('#dataPrevBtn').prop('disabled', true);
        }
        else{
            $('#dataPrevBtn').prop('disabled', false);
        }
        if($('#limit_container select').val() !== 'none') {
            if(parseInt($('#limit_container select').val()) - parseInt($('#offset_input').val())  <= 50 ){
                $('#dataNextBtn').prop('disabled', true);
            }
        }

    }

    /* Hotkeys */
    document.addEventListener("keydown", function (e) {
        if (e.keyCode == 83 && e.ctrlKey) { //Ctrl+S key pressed
            QueryToolbox.save(function (id) {}, 0);

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


    function reset(){
        $('.value-remove-btn').click();
        $('#selected_dimensions > option').remove();
        $('#id_category > option').remove();
        $('#id_orderby > option').remove();
        $('#resetMapBounds').click();
        $('#chart-filters > .filter').remove();

        // $('#lat_min').val("").trigger('change');
        // $('#lat_max').val("").trigger('change');
    }

    // export
    window.QueryToolbox = QueryToolbox;
});