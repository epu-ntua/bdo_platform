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
    // var expressionTable = expressionAndOperationTable.filter(expr => expr.startsWith("F"));
    // var operatorTable = expressionAndOperationTable.filter(expr => !expr.startsWith("F"));
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

function load_filters(filters, doc) {
    if (filters['op'] && (filters['op'] === "AND")){
        $("#filters-expr-type").val('ALL_AND').trigger("change");
        load_filters(filters['a'], doc);
        load_filters(filters['b'], doc);
    }
    else if (filters['op'] && (filters['op'] === "OR")){
        $("#filters-expr-type").val('ALL_OR').trigger("change");
        load_filters(filters['a'], doc);
        load_filters(filters['b'], doc);
    }
    else if (filters['op']){
        if (filters['op'] === "inside_rect"){
            var min_values = filters['b'].split("<<")[1].split(">,<")[0];
            var max_values = filters['b'].split(">,<")[1].split(">>")[0];
            $("#lat_min").val(min_values.split(",")[0]);
            $("#lon_min").val(min_values.split(",")[1]);
            $("#lat_max").val(max_values.split(",")[0]);
            $("#lon_max").val(max_values.split(",")[1]);
            setTimeout(function(){$("#lat_min, #lon_min, #lat_max, #lon_max").trigger("change");}, 1000);
        }
        else if ((filters['op'] === "gte_time") && (filters['a'].split(/_(.+)/)[1] === "time")){
            $("#startdatepicker input").val(String(filters['b']).slice(1,-1));
            $('#startdatepicker').datetimepicker("update", new Date(Date.parse(String(filters['b']).slice(1,-1))));
            // console.log(filters['b']);
            // console.log(Date.parse(filters['b']));
            // console.log(new Date(Date.parse(filters['b'])));
            startdate = $('#startdatepicker input').val();
        }
        else if ((filters['op'] === "lte_time") && (filters['a'].split(/_(.+)/)[1] === "time")){
            $('#enddatepicker').datetimepicker("update", new Date(Date.parse(String(filters['b']).slice(1,-1))));
            enddate = $('#enddatepicker input').val();
        }
        else{
            var a, a_forVariable, a_title, a_type;
            $.each(doc['from'], function (f_index, _f) {
                if(parseInt(filters['a'].split(/_(.+)/)[0].slice(1)) === f_index) {
                    $.each(_f['select'], function (_, _s) {
                        if (_s['type'] === "VALUE") {
                            if(filters['a'] === _s['name']){
                                a = parseInt(_f['type']);
                                a_type = "variable";
                                a_title = _s['title'];
                                a_forVariable = parseInt(_f['type']);
                            }
                        }
                        else {
                            if(filters['a'] === _s['name']){
                                a = parseInt(_s['type']);
                                a_type = "dimension";
                                a_title = _s['title'];
                                a_forVariable = parseInt(_f['type']);
                            }
                        }
                    });
                }
            });
            var last_filter = 0;
            $.each(Object.keys(QueryToolbox.filters), function (_, fName) {
                if(last_filter < parseInt(String(fName).split('F')[1])){
                    last_filter = parseInt(String(fName).split('F')[1])
                }
            });
            var filterName = 'F' + (last_filter + 1);
            var filter_b;
            // console.log(filters['b']);
            if (String(filters['b']).indexOf("'") > -1){
                filter_b = filters['b'].slice(1, -1)
            }
            else{
                filter_b = filters['b']
            }
            QueryToolbox.filters[filterName]= {
                a: a,
                a_forVariable: a_forVariable,
                a_title: a_title,
                a_type: a_type,
                b: filter_b,
                filter_string: a_title + ' ' + $("#filters-modal #new-filter-operator option[value='"+filters['op']+"']").text() + ' ' + filters['b'],
                op: filters['op']
            };
        }
    }
}

$(function () {
    /* `QueryToolbox` is the object responsible for the behaviour of the Toolbox Charts component */
    var QueryToolbox = {
        // The user selection
        variables: [],
        groupings: [],
        orderings: [],
        temporal_resolution: '',
        spatial_resolution: '',
        filters: [],
        common_dimensions: [],
        datasets: [],
        dataset_names: [],

        // the Query Toolbox objects, only one is created
        objects: [],
        /* Initialisation (it is called from the template) */
        addChart: function (chartFilters, chartPolicy, queryId, queryTitle) {
            // Add the title of the query
            queryTitle = queryTitle || '';
            // Create a new object
            var obj = {
                'queryId': queryId,
                'tempQueryId': queryId,
                'queryTitle': queryTitle
            };
            this.objects=[obj];
            // add tab
            $('#chart-picker').html('<p style="display: inline-block;"><span class="queryTitle">'+queryTitle+'</span></p>');
            // mark tab as unsaved for new charts
            if (typeof(queryId) === 'undefined') {
                this.tabMarker.currentUnsaved();
            }
            // set chart options (category/value fields) & filters
            this.initChartOptions(obj);
            // show name field
            // $('#chart-name').removeClass('hidden').find('input').val(queryTitle);
            $('#chart-name').find('input').val(queryTitle);
        },

        setChartOptions: function (obj, chartFilters, chartPolicy) {
            obj.$chartFilters = $(chartFilters);
            obj.chartPolicy = chartPolicy;
        },

        /* Load the required initial information from the platform */
        initChartOptions: function (obj) {
            var that = this;
            $.ajax({
                url: '/queries/simplified/config/',
                success: function (chartPolicy) {
                    that.setChartOptions(obj, '', chartPolicy)
                }
            })
        },


        // *** ADD - REMOVE VARIABELS ***
        /* Creates an option selected variable fieldset */
        addVariableField: function (config) {
            var obj = QueryToolbox.objects[0];

            // create the aggregation options on the left of each new variable
            var $aggregateSelect = $('<select name="field_aggregate" />');
            var cnt = 0;
            $.each(obj.chartPolicy.aggregates, function(idx, aggregate) {
                if ((aggregate.typelist.indexOf(config.datatype) >= 0) || (config.datatype === "None") ){
                    cnt+=1;
                    // create aggregate option
                    var $option = $('<option />').text(aggregate.title).attr('value', aggregate.value);
                    // if resolution or groupby is eneabled disable -noaggregate option and set default aggregate function AVG
                    if ((QueryToolbox.groupings.length > 0) || ($("#spatial_resolution").val() !== '') || ($("#temporal_resolution").val() !== '')) {
                        if (aggregate.title === "(No aggregate)") {
                            $option.attr('disabled', 'disabled')
                        }
                        if (cnt === 2) {
                            $option.attr("selected", "selected");
                        }
                    }
                    // add to aggregate select
                    $aggregateSelect.append($option);
                }
            });

            var $fieldInputShown = $('<input class="form-control" readonly style="width: 100%; height: 100%; margin: 2px 0; padding-left: 5px; background-image: none; border: #b4b4b4; border-width: 1px; border-style: solid; border-radius: 5px"/>')
            $fieldInputShown.attr('data-variable-id', config.id);
            $fieldInputShown.val(config.title + ' (' + config.unit + ')');

            var $fieldInput = $('<input class="hidden" style="width: 100%; height: 100%;"/>').attr('name', 'variable_field');
            $fieldInput.attr('data-variable-id', config.id);
            $fieldInput.attr('data-datatype-id', config.datatype);
            $fieldInput.val(config.name);


            // set field value
            var $fieldset = $('<div class="fieldset">' +config.label+'<br />' + '<div class="row" style="margin: 0"><div class="col-xs-5 col-prefix" style="padding: 0;' +'">' + '</div><div class="col-xs-10 col-main" style="padding: 0;"></div><div class="col-xs-1 col-suffix"></div></div></div>');
            $fieldset.find('.col-main').append($fieldInput);
            $fieldset.find('.col-main').append($fieldInputShown);

            $fieldset.find('.col-prefix').append($aggregateSelect);

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

        /* Remove a value field */
        removeVariableField: function ($fieldset) {
            // remove the fieldset
            $fieldset.remove();

            // if no variable fields are selected, hide the QD fields
            if($("[name='variable_field']").length === 0){
                $('.after-data-selection').each(function () {
                    $(this).hide();
                });
                $('.before-data-selection').each(function () {
                    $(this).show();
                });
                $('.chartdiv').hide();
                $('#paginationDiv').hide();
                var $table = $("#graph-data-table");
                $table.find('thead').empty();
                $table.find('tbody').empty();
                reset();
            }
        },


        // *** QUERY DOC AND QUERY EXECUTION ***
        // TODO: This function may change, in order to get the info from the initial fields of the Toolbox
        _getChartInfo: function () {
            var values = [], columns = [];
            var vfs = $('input[name="variable_field"]');

            $.each(vfs, function (idx, vf) {
                // create the field name (including the aggregate)
                var aggregate = $(vf).closest('.row').find('*[name="field_aggregate"]').val();
                // if aggregate property was not found
                if (typeof(aggregate) === "undefined") {
                    aggregate = 'AVG'
                }
                var fname = $(vf).val();
                values.push({
                    name: fname,
                    type: $(vf).attr('data-variable-id'),
                    aggregate: aggregate
                });
                // field title
                var ttl_prefix = '';
                if (aggregate != '') {
                    ttl_prefix = $('select[name="field_aggregate"] option[value="' + aggregate + '"]').get(0).textContent + ' '
                }
                var ttl = ttl_prefix + $(vf).val();
                // keep the title of the field for the data table
                columns.push({name: fname, title: ttl});
            });
            return {
                values: values,
                columns: columns
            };
        },

        generateQueryDoc: function() {
            var info = this._getChartInfo();
            console.log(info);
            // The initial structure of the query document
            var result = {
                from: [],
                distinct: false,
                offset: 0,
                "limit": ($('#limit_container select').val() !== 'none')? parseInt($('#limit_container select').val()) : [],
                "orderings": []
            };
            this.create_grouping_list();
            // for each variable
            $.each(QueryToolbox.variables, function(idx, variable) {
                var _from = {
                    // "type" in "from" field of the document is the variable id
                    type: variable.id,
                    // "name" in "from" field of the document is the variable's name, with an underscore and its order in the document
                    name: variable.name + '_' + String(idx),
                    // "select" in "from" field of the document is the columns that will be selected from the table where the variable is
                    select: []
                };

                // push main variable - THE VARIABLES in the query document have as "type" the string "VALUE"
                _from.select.push({
                   type: 'VALUE',
                   name: 'i' + String(idx) + '_' + variable.name,
                   title: variable.title,
                   datatype: variable.datatype,
                   aggregate: variable.aggregate,
                   groupBy: false,
                   exclude: false
                });

                // push dimensions
                $.each(variable.dimensions, function(jdx, dim) {
                    var name = dim.name;
                    var groupBy = false;
                    $.each(QueryToolbox.groupings, function (_, elem) {
                       if(parseInt(dim.id) === parseInt(elem.dimension_id)){
                           groupBy = true;
                           return false;
                       }
                    });
                    var dimAggregate = '';

                    // if spatial resolution is used
                    if ((name === 'latitude') || (name === 'longitude')) {
                        if (QueryToolbox.spatial_resolution !== ""){
                            groupBy = true;
                            if ($("#spatial_resolution").val() === "1")
                                dimAggregate = 'round0';
                            else if($("#spatial_resolution").val() === "0.1")
                                dimAggregate = 'round1';
                            else if($("#spatial_resolution").val() === "0.01")
                                dimAggregate = 'round2';
                        }
                    }
                    // if temporal resolution is used
                    if (name === 'time') {
                        if (QueryToolbox.temporal_resolution !== ""){
                            groupBy = true;
                            if($("#temporal_resolution").val() === "hour")
                                dimAggregate = 'date_trunc_hour';
                            else if($("#temporal_resolution").val() === "day")
                                dimAggregate = 'date_trunc_day';
                            else if($("#temporal_resolution").val() === "month")
                                dimAggregate = 'date_trunc_month';
                        }
                    }

                    var dimension = {
                        type: dim.id,
                        name: 'i' + String(idx) + '_' + name,
                        title: dim.title,
                        datatype: dim.datatype,
                        groupBy: groupBy,
                        aggregate: dimAggregate,
                        exclude: !groupBy && variable.aggregate
                    };
                    // check if joined
                    if (idx > 0) {
                        $.each(result.from[0].select, function(kdx, d) {
                            var dimName = d.name.split('_').slice(1).join('_');
                            // TODO: Check this condition for joining dimensions
                            if (
                                (dimName === name) ||
                                (
                                    (['lat', 'lon'].indexOf(name.substr(0, 3)) >= 0) &&
                                    (dimName.substr(0, 3) === name.substr(0, 3))
                                )
                            ) {
                                dimension.joined = d.name;
                                dimension.exclude = true;
                                return false;
                            }
                        })
                    }
                    _from.select.push(dimension);

                    $.each(QueryToolbox.orderings, function (oidx, elem) {
                        if((elem.type === "dimension") && (parseInt(elem.dimension_id) === parseInt(dim.id))) {
                            result.orderings.push({type: elem.ordering, name: 'i' + String(idx) + '_' + name});
                        }
                    });
                });
                // add to query
                result.from.push(_from);

                $.each(QueryToolbox.orderings, function (oidx, elem) {
                    if((elem.type === "variable") && (parseInt(elem.variable_id) === parseInt(variable.id))) {
                        result.orderings.push({type: elem.ordering, name: 'i' + String(idx) + '_' + variable.name});
                    }
                });
            });
            // add filters
            result.filters = this.constructFiltersParam(result);

            return result;
        },

        /* Gets the data based on the fields & options selected by the user */
        fetchQueryData: function () {

            var doc = this.generateQueryDoc();
            if (doc.from.length === 0) {
                return
            }
            doc['limit'] = 500;
            // get category, values info & filters
            var filterStr = this.constructFiltersParam();

            // request data
            var runQuery = function(id) {
                // update data table headers & data
                var $table = $("#graph-data-table");
                $table.find('thead').empty();
                $table.find('tbody').empty();
                $("#cancel-query-btn").show();
                var xhr = $.ajax({
                    url: '/queries/execute/',
                    type: 'POST',
                    data: {
                        query: JSON.stringify(doc),
                        csrfmiddlewaretoken: $('[name="csrfmiddlewaretoken"]').val()
                    },
                    success: function (response) {
                        $("#cancel-query-btn").hide();
                        $('.no-data-message').hide();
                        $('#chartdiv').show();
                        $('#paginationDiv').show();

                        var iframe = $('<iframe  onload="hide_gif();" />');
                        $("#viz_container iframe").remove();
                        $("#viz_container").append(iframe);

                        if(response.hasOwnProperty('error_message')) {
                            console.log(response['error_message']);
                            hide_gif();
                            $('#chartdiv').hide();
                            $('#paginationDiv').hide();
                            $('.no-data-message').show();

                            $('#error_message_span').html(response['error_message']);
                            $('#error_message_alert').show();
                        }
                        else {
                            var $header = $('<tr />');
                            console.log(response);
                            $.each(response.headers.columns, function (idx, col) {
                                $header.append($('<td />').text(col.title + "\n(" + col.unit + ")").css({"white-space":"pre-line"}))
                            });
                            $table.find('thead').append($header);
                            var limit = 50;
                            var lastPage = 0;
                            $.each(response.results, function (idx, res) {
                                lastPage = Math.floor(idx/limit);
                                var $row = $('<tr '+(lastPage === 0 ? '' : 'hidden')+ ' page="'+ lastPage+'"/>');
                                $.each(res, function (jdx, resItem) {
                                    $row.append($('<td />').text(resItem));
                                });
                                $table.find('tbody').append($row);
                            });
                            $("#paginationDiv").attr("lastPage",lastPage);
                            updatePaginationButtons();
                            $("#chart-content-tabs li").eq(1).find('a').click();
                            $("#chart-content-tabs li").eq(0).find('a').click();
                        }
                    },
                    error: function (response) {
                        console.log(response['error_message']);
                        $("#cancel-query-btn").hide();
                        hide_gif();
                        $('#chartdiv').hide();
                        $('#paginationDiv').hide();
                        $('.no-data-message').show();
                        alert('We are sorry, an error occurred.');
                    }
                });
                $("#cancel-query-btn").click(function () {
                    xhr.abort();
                    $(this).prop("onclick", null).off("click");
                })
            };

            // hack due to visualizations needing the query id
            // first save
            QueryToolbox.save(runQuery, 1);
        },
        create_grouping_list: function () {
            var grouping_list=[];
            $.each(QueryToolbox.groupings, function (_, elem) {
                grouping_list.push(elem.dimension_name);
            });
            if (QueryToolbox.temporal_resolution !== ""){
                grouping_list.push('time');
            }
            if (QueryToolbox.spatial_resolution !== "") {
                grouping_list.push('latitude');
                grouping_list.push('longitude');
            }
            if (grouping_list.length>0) {
                $.each(QueryToolbox.orderings, function (index, elem) {
                    if (!(grouping_list.includes(elem.name))) {
                        QueryToolbox.orderings.splice(index,1);
                        var $sel =  $('[name="orderby"] option[data-name="'+ String(elem.name) +'"]');
                        $sel.prop('selected', false);
                        $sel.removeAttr('disabled');
                        refresh_selects2();
                    }
                });
            }

        },


        // *** TABS - LOAD - SAVE - RENAME ***
        tabMarker: {
            currentUnsaved: function () {
                var $active = $('#chart-picker p');
                // check if already marked
                if ($active.find('.unsaved').length > 0) {
                    return
                }
                // mark as unsaved
                $active.append('<span class="unsaved">*</span>');
            },
            currentSaved: function () {
                $('#chart-picker p').find('.unsaved').remove();
            }
        },

        /* Get the `CSRF` token */
        getCsrfMiddlewareToken: function () {
            return $('#chart-container input[name="csrfmiddlewaretoken"]').val()
        },

        /* Save the current query */
        save: function (callback, temp) {
            // csrf token
            var data = {
                csrfmiddlewaretoken: this.getCsrfMiddlewareToken(),
                document: JSON.stringify(this.generateQueryDoc()),
                title: this.objects[0].queryTitle,
                v2_fields: [],
                v2_options: this.objects[0].$chartFilters.html()
            };

            // send the save request
            var that = this;
            var url;
            if (temp === 1){
                url = '/queries/save/' + (this.objects[0].tempQueryId ? this.objects[0].tempQueryId + '/' : '') + '1/'
            }
            else{
                url = '/queries/save/' + (this.objects[0].queryId ? this.objects[0].queryId + '/' : '') + '0/'
            }
            $.ajax({
                url: url,
                type: 'POST',
                data: data,
                success: function (data) {
                    // save id & mark
                    if (temp === 1){
                        that.objects[0].tempQueryId = Number(data.pk);
                    }
                    else{
                        that.objects[0].queryId = Number(data.pk);
                        $('#query-id-li a #query--id').text(data.pk);
                    }
                    that.tabMarker.currentSaved();

                    // update status
                    $('#selected_query').val(parseInt(data.pk));
                    // $('#selected_query').val(parseInt(data.pk));
                    // run callback
                    if (callback) {
                        callback(data.pk)
                    }
                    if (temp === 0) {
                        $.notify({
                            icon: "add_alert",
                            message: "Query: " + QueryToolbox.objects[0].queryTitle + " saved successfully!"

                        }, {
                            type: 'success',
                            timer: 1000,
                            placement: {
                                from: 'top',
                                align: 'right'
                            }
                        });
                    }
                }
            });
        },

        /* Load an existing query */
        load: function (queryId) {
            $("#new-query").click();
            $.ajax({
                url: '/queries/load/' + queryId + '/',
                type: 'GET',
                success: function (data) {
                    var doc = data.document;
                    var selection = [];
                    $.each(doc['from'], function (_, _f) {
                        var id = _f['type'];
                        var dims = [];
                        var name, title, datatype, unit, aggregate, groupBy, dataset_id, dataset_size, dataset_name, dataset_lat_min, dataset_lat_max, dataset_lon_min, dataset_lon_max, dataset_time_min, dataset_time_max;
                        $.each(_f['select'], function (_, _s) {
                            if (_s['type'] === "VALUE"){
                                name = String(_s['name']).split(/_(.+)/)[1];
                                title = _s['title'];
                                datatype = _s['datatype'];
                                dataset_id = $("#select-data-modal #dataset-list-section .dataset-variables-div li[data-variable-id='"+id+"']").data("variable-dataset");
                                dataset_size = $("#select-data-modal #dataset-list-section .dataset-section .dataset-name[data-dataset-id='"+dataset_id+"']").closest(".dataset-section").find(".dataset-metadata .dataset-size td").eq(1).text();
                                dataset_name = $("#select-data-modal #dataset-list-section .dataset-section .dataset-name[data-dataset-id='"+dataset_id+"']").closest(".dataset-section").find(".dataset-name .dataset-title").text();
                                dataset_lat_min = $("#select-data-modal #dataset-list-section .dataset-section .dataset-name[data-dataset-id='"+dataset_id+"']").closest(".dataset-section").find(".dataset-coverage-div").find(".lat_from").text();
                                dataset_lat_max = $("#select-data-modal #dataset-list-section .dataset-section .dataset-name[data-dataset-id='"+dataset_id+"']").closest(".dataset-section").find(".dataset-coverage-div").find(".lat_to").text();
                                dataset_lon_min = $("#select-data-modal #dataset-list-section .dataset-section .dataset-name[data-dataset-id='"+dataset_id+"']").closest(".dataset-section").find(".dataset-coverage-div").find(".lon_from").text();
                                dataset_lon_max = $("#select-data-modal #dataset-list-section .dataset-section .dataset-name[data-dataset-id='"+dataset_id+"']").closest(".dataset-section").find(".dataset-coverage-div").find(".lon_to").text();
                                dataset_time_min = $("#select-data-modal #dataset-list-section .dataset-section .dataset-name[data-dataset-id='"+dataset_id+"']").closest(".dataset-section").find(".dataset-coverage-div").find(".time_from").text();
                                dataset_time_max = $("#select-data-modal #dataset-list-section .dataset-section .dataset-name[data-dataset-id='"+dataset_id+"']").closest(".dataset-section").find(".dataset-coverage-div").find(".time_to").text();
                                unit = $("#select-data-modal #dataset-list-section .dataset-variables-div li[data-variable-id='"+id+"']").data("variable-unit");
                                aggregate = _s['aggregate'];
                                groupBy = _s['groupBy'];
                            }
                            else{
                                dims.push({id: _s['type'], name: String(_s['name']).split(/_(.+)/)[1], title: _s['title'], datatype: _s['datatype']});
                            }
                        });
                        selection.push({
                            id: id,
                            name: name,
                            title: title,
                            datatype: datatype,
                            dataset_id: dataset_id,
                            dataset_size: dataset_size,
                            dataset_name: dataset_name,
                            dataset_lat_min: dataset_lat_min,
                            dataset_lat_max: dataset_lat_max,
                            dataset_lon_min: dataset_lon_min,
                            dataset_lon_max: dataset_lon_max,
                            dataset_time_min: dataset_time_min,
                            dataset_time_max: dataset_time_max,
                            unit: unit,
                            aggregate: aggregate,
                            groupBy: groupBy,
                            dimensions: dims
                        })
                    });
                    console.log(doc);
                    console.log(selection);
                    console.log(QueryToolbox.groupings);
                    add_selection(selection);
                    var $categorySelectField = $('[name="category"]');
                    var $spatial_resolution_field = $('#spatial_resolution');
                    var $temporal_resolution_field = $('#temporal_resolution');
                    $.each(doc['from'], function (_, _f) {
                        var id = _f['type'];
                        $.each(_f['select'], function (_, _s) {
                            if (_s['type'] === "VALUE"){

                            }
                            else{
                                if (_s['groupBy'] === true){
                                    if ((_s['name'].split(/_(.+)/)[1] !== "latitude") && (_s['name'].split(/_(.+)/)[1] !== "longitude") && (_s['name'].split(/_(.+)/)[1] !== "time"))
                                        $categorySelectField.find("option[value='"+ _s['type'] +"']").attr('selected', 'selected');
                                }
                                if ((_s['name'].split(/_(.+)/)[1] === "latitude") || (_s['name'].split(/_(.+)/)[1] === "longitude")){
                                    if (_s['aggregate'].startsWith("round")){
                                        if(_s['aggregate'].slice(-1) === "0")
                                            $spatial_resolution_field.val("1");
                                        else if (_s['aggregate'].slice(-1) === "1")
                                            $spatial_resolution_field.val("0.1");
                                        else if (_s['aggregate'].slice(-1) === "2")
                                            $spatial_resolution_field.val("0.01");
                                    }
                                    else{
                                        $spatial_resolution_field.val("");
                                    }

                                }
                                if (_s['name'].split(/_(.+)/)[1] === "time"){
                                    if (_s['aggregate'].startsWith("date_trunc")){
                                        $temporal_resolution_field.val(_s['aggregate'].split("date_trunc_")[1]);
                                    }
                                    else{
                                        $temporal_resolution_field.val("");
                                    }

                                }
                            }
                        })
                    });
                    setTimeout(function(){$('[name="category"]').trigger("change");}, 1000);
                    setTimeout(function(){$('#spatial_resolution').trigger("change");}, 1000);
                    setTimeout(function(){$('#temporal_resolution').trigger("change");}, 1000);

                    var $order_by_field = $('#id_order');
                    $.each(doc['orderings'], function (_, _ordering) {
                        $order_by_field.find("option[data-name='"+ _ordering['name'].split(/_(.+)/)[1] +"'][data-ordering='"+ _ordering['type'] +"']").attr('selected', 'selected');
                    });
                    setTimeout(function(){$('#id_order').trigger("change");}, 1000);

                    var filters = doc['filters'];
                    load_filters(filters, doc);
                    $(".filter-counter").text(Object.keys(QueryToolbox.filters).length);

                    QueryToolbox.objects[0].queryId = data.pk;
                    QueryToolbox.rename(data.title);
                    $("#chart-name input").val(data.title);
                    setTimeout(function(){QueryToolbox.tabMarker.currentSaved();}, 1500);
                },
                error: function (xhr, status, error) {
                    console.log(error)
                }
            });
        },

        rename: function (title) {
            this.objects[0].queryTitle = title;
            $('#query-name-li a #query--title').text(title);
            $("#query-save-name").val(title);
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
                    width: '60vw',
                    // height: '50vh',
                    // top: '30px'
                });
                $modalBody.css('height', '60vh');
                $modalBody.closest('.ui-dialog').css('top', '30px');
                // get the user's charts
                $.ajax({
                    url: '/queries/simplified/list/',
                    type: 'GET',
                    success: function (data) {
                        $modalBody.html(data);
                        $modalBody.find('th').css('text-align', 'center');
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



        // *** FILTERS ***
        getFilterArray: function () {
            // return QueryToolbox.filters;
            var filters = [];
            $.each(Object.keys(QueryToolbox.filters), function (fidx, fkey) {
                filters.push(QueryToolbox.filters[fkey])
            });
            return filters
            // var filters = [];
            // $.each($('#chart-filters > .filter'), function (idx, flt) {
            //     var $flt = $(flt);
            //     filters.push({
            //         'name': $flt.data('name'),
            //         'title': $flt.data('title'),
            //         'a': $flt.data('a'),
            //         'op': $flt.data('op'),
            //         'b': $flt.data('b')
            //     });
            // });
            //
            // return filters
        },

        constructFiltersParam: function (queryDocument) {
            if (queryDocument === undefined) {
                return
            }

            // gather individual filters
            var filters = this.getFilterArray();


            // if (startdate !== null){
            //     if (time_dim_id !== null) {
            //         filters.push({a: time_dim_id, op: 'gte', b: startdate.toString()});
            //     }
            // }
            // if (enddate !== null){
            //     if (time_dim_id !== null) {
            //         filters.push({a: time_dim_id, op: 'lte', b: enddate.toString()});
            //     }
            // }

            var filterTree = {};

            var expression = $('#filters-expr-input').val();
            var exprType = $('#chart-filters > .filter-expr').attr('data-expr_type');
            var customExpressionMap = {};

            // $.each(Object.keys(QueryToolbox.filters), function (idx, fkey) {
            $.each(filters, function (fdx, filter) {
                    // var filter = QueryToolbox.filters[fkey];
                    var aName;
                    var datatype='';
                    $.each(queryDocument.from, function (idx, _from) {
                        $.each(_from.select, function (jdx, attr) {
                            if (attr.type === "VALUE") {
                                // if (String(attr.name).split(new RegExp("i[0-9]+_"))[1] === filter.a) {
                                if ((filter.a_type === "variable") && (parseInt(_from.type) === parseInt(filter.a))) {
                                    aName = attr.name;
                                    datatype = attr.datatype;
                                }
                            }
                            else {
                                if ((filter.a_type === "dimension") && (parseInt(attr.type) === parseInt(filter.a))) {
                                    aName = attr.name;
                                    datatype = attr.datatype;
                                }
                            }
                        })
                    });
                    var newFilter;
                    if (filter.op === "not_null"){
                        newFilter = {
                            a: aName,
                            op: filter.op,
                            b: ""
                        };
                    }
                    else{
                        if (datatype == "STRING" ) {
                            newFilter = {
                                a: aName,
                                op: filter.op,
                                b: "'" + filter.b + "'"
                            };

                        }
                        else if(datatype == "TIMESTAMP" ){
                            newFilter = {
                                a: aName,
                                op: filter.op,
                                b: " timestamp '"+filter.b+"'"
                            };
                        }
                        else{
                            newFilter = {
                                a: aName,
                                op: filter.op,
                                // b: typeof(filter.b) === 'string' ? "'" + filter.b + "'" : filter.b
                                b: parseFloat(filter.b)
                            };
                        }
                    }


                    if (exprType === 'CUSTOM') {
                        var mapIndex = fdx + 1;
                        customExpressionMap["F" + mapIndex] = newFilter;
                    } else {
                        if (fdx === 0) {
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

            // Gather temporal filters
            var time_dim_id = null;
            $.each(QueryToolbox.variables, function (vidx, variable) {
                $.each(variable.dimensions, function (didx, dimension) {
                    if(dimension.name === 'time'){
                        time_dim_id = dimension.id
                    }
                });
            });
            var time_name;
            $.each(queryDocument.from, function (idx, _from) {
                $.each(_from.select, function (jdx, attr) {
                    if (attr.type !== "VALUE") {
                        if (time_dim_id !== null) {
                            if (parseInt(attr.type) === parseInt(time_dim_id)) {
                                time_name = attr.name;
                            }
                        }
                    }
                })
            });

            // Gather spatial filters
            var latitude_dim_id = null;
            var longitude_dim_id = null;
            $.each(QueryToolbox.variables, function (vidx, variable) {
                $.each(variable.dimensions, function (didx, dimension) {
                    if(dimension.name === 'latitude'){
                        latitude_dim_id = dimension.id
                    }
                    if(dimension.name === 'longitude'){
                        longitude_dim_id = dimension.id
                    }
                });
            });
            if (startdate !== null){
                if (time_dim_id !== null) {
                    newFilter = {
                        a: time_name,
                        op: 'gte_time',
                        b: "'" + startdate.toString() + "'"
                    };
                    if (Object.keys(filterTree).length === 0) {
                        filterTree = newFilter;
                    }
                    else {
                        filterTree = {
                            a: newFilter,
                            op: 'AND',
                            b: JSON.parse(JSON.stringify(filterTree))
                        };
                    }
                }
            }

            if (enddate !== null){
                if (time_dim_id !== null) {
                    // filters.push({a: time_dim_id, op: 'lte', b: enddate.toString()});
                    newFilter = {
                        a: time_name,
                        op: 'lte_time',
                        b: "'" + enddate.toString() + "'"
                    };
                    if (Object.keys(filterTree).length === 0) {
                        filterTree = newFilter;
                    }
                    else {
                        filterTree = {
                            a: newFilter,
                            op: 'AND',
                            b: JSON.parse(JSON.stringify(filterTree))
                        };
                    }
                }
            }

            if ((bounds[0] !== -90) || (bounds[2] !== 90) || (bounds[1] !== -180) || (bounds[3] !== 180)){
                if ((latitude_dim_id !== null) && (longitude_dim_id !== null)) {
                    // filters.push({a: '<'+latitude_dim_id+','+longitude_dim_id+'>', op: 'inside_rect', b: '<<'+bounds[0].toString()+','+bounds[1].toString()+'>,<'+bounds[2].toString()+','+bounds[3].toString()+'>>'});
                    var newFilter = {
                        a: '<' + latitude_dim_id + ',' + longitude_dim_id + '>',
                        op: 'inside_rect',
                        b: '<<' + bounds[0].toString() + ',' + bounds[1].toString() + '>,<' + bounds[2].toString() + ',' + bounds[3].toString() + '>>'
                    };
                    if (Object.keys(filterTree).length === 0) {
                        filterTree = newFilter;
                    }
                    else {
                        filterTree = {
                            a: newFilter,
                            op: 'AND',
                            b: JSON.parse(JSON.stringify(filterTree))
                        };
                    }
                }
            }


            // console.log(filters);

            return filterTree;
        },

        /* Responsible for editing queryset filters */
        filterManager: {
            /* Loads the appropriate information inside the popup */
            load: function () {
                // find active chart
                var current = 0;
                var obj = QueryToolbox.objects[current];
                var filters = QueryToolbox.getFilterArray();

                // get the modal
                var $filterModal = $('#filters-modal');

                // set modal title
                $filterModal.find('.chart-title').text(obj.queryTitle);

                // show/hide expression settings
                var $filterExprSettings = $filterModal.find('#filter-expr-settings');
                if (Object.keys(QueryToolbox.filters).length > 1) {
                    $filterExprSettings.show();
                } else {
                    $filterExprSettings.hide();
                }

                // show filters
                var $filterTable = $filterModal.find('table');
                var $filterTableBody = $filterTable.find('tbody');
                $filterTableBody.empty();
                if (Object.keys(QueryToolbox.filters).length == 0) {
                    var $placeholderRow = $('<tr class="placeholder-row"><td>-</td><td><em>' + 'No filters found' + '</em></td><td></td></tr>');
                    $filterTableBody.append($placeholderRow);
                } else {
                    $.each(Object.keys(QueryToolbox.filters), function (fidx, fkey) {
                        var filter = QueryToolbox.filters[fkey];
                        var $filterTr = $('<tr><td>' + fkey + '</td><td>' + filter.filter_string + '</td><td><div class="remove-filter-btn"><i class="fa fa-times"></i></div></td></tr>');
                        $filterTableBody.append($filterTr);
                    });
                }


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
                var close_btn = $('.ui-button.ui-corner-all.ui-widget.ui-dialog-titlebar-close');
                $(close_btn).removeClass('ui-button-icon-only');
                $(close_btn).text('');
                $(close_btn).append('<span class="fas fa-times"></span>');
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

                // INSTEAD OF CALLING THE BACK-END
                var data = {'type': 'text'};
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
                if($filterOperand.val() === "not_null"){
                    $input.val("");
                    $input.prop("readonly", true);
                    $input.css({"display": "none"});
                }
                else{
                    $input.val("");
                    $input.prop("readonly", false);
                    $input.css({"display": "block"});
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

                // get options, comparison type & input type from the backend
                // $.ajax({
                //     url: url,
                //     type: 'GET',
                //     success: function (data) {
                //         var $input,
                //             $filterOperand = $('#new-filter-operator'),
                //             opSelector = 'option[value="<"], option[value="<="], option[value=">"], option[value=">="]';
                //
                //         if (data.options) {
                //             $input = $('<select name="new-filter-value" />');
                //             $.each(data.options, function (idx, option) {
                //                 var val = option.value;
                //                 if (typeof(val) === 'string') {
                //                     val = "'" + val + "'";
                //                 }
                //
                //                 $input.append('<option value="' + val + '">' + option.name + '</option>');
                //             });
                //
                //             // update operands
                //             $filterOperand.select2()
                //         }
                //
                //         else if (data.type === 'number') {
                //             $input = $('<input type="number" name="new-filter-value" />');
                //         }
                //         else {
                //             $input = $('<input type="text" name="new-filter-value" />');
                //         }
                //         if($filterOperand.val() === "not_null"){
                //             $input.val("");
                //             $input.prop("readonly", true);
                //             $input.css({"display": "none"});
                //         }
                //         else{
                //             $input.val("");
                //             $input.prop("readonly", false);
                //             $input.css({"display": "block"});
                //         }
                //
                //         // enable/disable operators
                //         if (data.orderable) {
                //             $filterOperand.find(opSelector).removeAttr('disabled');
                //         } else {
                //             $filterOperand.find(opSelector).attr('disabled', 'disabled');
                //         }
                //         $filterOperand.select2();
                //
                //         $inputContainer.append($input);
                //         if (data.options) {
                //             $input.select2();
                //         }
                //
                //         // show help message
                //         var message = '';
                //         if (data.orderable && (typeof(data.min) !== 'undefined')) {
                //             message += 'Minimum value: ' + String(data.min)
                //         }
                //         if (data.orderable && (typeof(data.min) !== 'undefined')) {
                //             message += 'Maximum value: ' + String(data.max)
                //         }
                //         $info.text(message);
                //     },
                //     error: function (xhr, status, error) {
                //         console.log(error)
                //     }
                // });
            },

            addFilter: function () {
                // add the new filters
                var filterColumnId = parseInt($('#new-filter-variable').find("option:selected").data('id'));
                var filterColumnType = $('#new-filter-variable').find("option:selected").data('type');
                var filterColumnTitle = $('#new-filter-variable').find("option:selected").data('title');
                var filterColumnforVariable = $('#new-filter-variable').find("option:selected").data('forvariable');
                var filterOperator = $('#new-filter-operator').val();
                var filterOperatorSymbol = $('#new-filter-operator option:selected').text();
                var filterValue = $('[name="new-filter-value"]').val();

                if (filterColumnType === "variable")
                        filterColumnTitle = $('#new-filter-variable').find("option:selected").text();

                // What is displayed as filter
                var filterStr = filterColumnTitle + ' ' + filterOperatorSymbol + ' ' + filterValue;

                // create filter name
                // find last filter
                var last_filter = 0;
                $.each(Object.keys(QueryToolbox.filters), function (_, fName) {
                    if(last_filter < parseInt(String(fName).split('F')[1])){
                        last_filter = parseInt(String(fName).split('F')[1])
                    }
                });
                var filterName = 'F' + (last_filter + 1);

                // add to filters
                $('#chart-filters').append('<div class="filter" data-name="' + filterName + '" data-title="' + filterStr +
                    '" data-a="' + filterColumnId +'" data-a_type="' + filterColumnType +'" data-a_title="' + filterColumnTitle +'" data-op="' + filterOperator + '" data-b="' + filterValue + '">' + filterStr + '</div>');

                QueryToolbox.filters[filterName] =
                    {
                        a: filterColumnId,
                        a_title: filterColumnTitle,
                        a_type: filterColumnType,
                        a_forVariable: filterColumnforVariable,
                        op: filterOperator,
                        b: filterValue,
                        filter_string: filterStr
                    };

                $(".filter-counter").text(Object.keys(QueryToolbox.filters).length);
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

            removeFilter: function (filterName, reload) {
                reload = reload || true;
                // remove the filter
                $('#chart-filters > .filter[data-name="' + filterName + '"]').remove();

                delete QueryToolbox.filters[filterName];
                $(".filter-counter").text(Object.keys(QueryToolbox.filters).length);

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
        }
    };



    // Add the select2 flieds
    $('#resolution select').select2();
    $('.query-controls-container select').select2({
        width: "100%",
        escapeMarkup: function(markup) {
            return markup;
        }
    });

    // $('.query-controls-container [name="orderby"]').on("change", function(e) {
    //     setTimeout(function(){ update_fields_when_ordering_asc_desc(); },100);
    // });

    // $('.query-controls-container [name="category"]').on("change", function(e) {
    //     setTimeout(function(){ update_fields_when_grouping(); },100);
    // });


    /* Filter dialog should always use select2 */
    $('#filters-modal select').select2();
    /* Limit input should use select2, with tags also */
    $('#limit_container select').select2({tags: true});
    // Group by select in data select modal
    $('#group-by-select').select2();
    // Aggregate select in data select modal
    $('#selection-aggregate').select2();


    $("#select-data-modal #dataset-filter-section select").select2({ width: '100%' });


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

    // function reset(){
    //     $('.value-remove-btn').click();
    //     $('#selected_dimensions > option').remove();
    //     $('#id_category > option').remove();
    //     $('#id_orderby > option').remove();
    //     $('#resetMapBounds').click();
    //     $('#chart-filters > .filter').remove();
    //
    //     // $('#lat_min').val("").trigger('change');
    //     // $('#lat_max').val("").trigger('change');
    // }
    // export
    window.QueryToolbox = QueryToolbox;
});