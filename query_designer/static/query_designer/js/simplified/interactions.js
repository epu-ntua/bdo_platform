$(function() {

    // *** DATA SELECTION MODAL *** //

    /* Close the data selection modal on cancel*/
    $('#selection-close-btn').on('click', function () {
        $('#select-data-modal').dialog('close');
    });

    /* Add a variable from the data selection modal */
    $('#selection-confirm-btn').on('click', function() {
        // The new variable to be added for query
        var newVariable = window.getDataSelection();


        /**
         * creates a hashmap with the dimension name as key and its frequency as value
         */
        function getDimensionFrequencyMap() {
            var dimensionMap = {};
            var $dimensions = $('#selected_dimensions option');
            $.each($dimensions, function () {
               var dimension = $(this).text();
               if (!(dimension in dimensionMap)){
                   dimensionMap[dimension] = 1;
               }
               else {
                   dimensionMap[dimension]++;
               }
            });
            return dimensionMap;
        }

        function getMaxFrequencyFromMap(frequencyMap) {
            var maxFreq = 0;
            for (var key in frequencyMap) {
                var currentValue = frequencyMap[key];
                if (currentValue > maxFreq)
                    maxFreq = currentValue;
            }
            return maxFreq;
        }

        /**
         * if a dimension is not included in all datasets then it is removed from the order by options
         */
        function removeUndesiredOrderByOptions() {
           var frequencyMap = getDimensionFrequencyMap();
           var maxFrequency = getMaxFrequencyFromMap(frequencyMap);
           var orderByOptions = $('[name="orderby"] option');
           $.each(orderByOptions, function () {
               var orderByOption = $(this).attr("data-type");
               if (frequencyMap[orderByOption] < maxFrequency)
                   $(this).remove();
           });
        }



        // Get the area of the Query Desinger where the new variable field will be added
        var $chartControls = $('#chart-control-list > .chart-control');
        // Add the label
        var label = 'Metric #<span class="metric-cnt">' + (QueryToolbox.variables.length+1) + '</span>';
        var obj = QueryToolbox.objects[0];

        // The new variable field
        var $fieldset = QueryToolbox.addVariableField({
            choices: obj.chartPolicy.variables,
            label: label,
            name: newVariable.name,
            title: newVariable.title,
            id: newVariable.id,
            unit: newVariable.unit,
            dimensions: newVariable.dimensions,
            canDelete: true
        });

        QueryToolbox.variables.push({
            id: newVariable.id,
            name: newVariable.name,
            title: newVariable.title,
            unit: newVariable.unit,
            aggregate: newVariable.aggregate,
            dimensions: newVariable.dimensions
        });
        // console.log(QueryToolbox.variables);

        // Update all the Query Designer fields (groupby, orderby, resolutions, filters according to the new set of selected variables
        updateQDfields();


        //if dimension is not included in all datasets then it is not desired
        removeUndesiredOrderByOptions();


        // add if any group by column was selected in the modal
        // var v = $category.val();
        // $.each(newVariable.groupBy, function (idx, f) {
        //     v.push(f);
        // });
        // $category.val(v).trigger('change.select2');



        // Select2 for the aggregation function
        $fieldset.find('select').select2();
        // add the new variable field
        $chartControls.append($fieldset);
        // show other query controls if at least one variable is selected
        if($chartControls.find('> *').length>0) {
            $('.after-data-selection').each(function () {
                $(this).show();
            });
        }
        // mark as unsaved
        QueryToolbox.tabMarker.currentUnsaved();

        // close popup
        $(".variable-list .selected").removeClass("selected");
        $("#selection-aggregate").val(null).trigger('change');
        $("#group-by-select").val(null).trigger('change');

    });

    /* When the data selection modal closes, hide the confirmation panel at the bottom of the panel */
    $('#select-data-modal').on('dialogclose', function(event) {
        $('.selection-confirm .col-xs-12').addClass('hidden');
    });




    // *** OPEN - LOAD - SAVE - RENAME QUERY *** //
    /* Add a new query - Reset the toolbox */
    $('#new-query').on('click', function () {
        reset();
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

    /* On chart rename */
    $('body').on('keyup', '#chart-name input', function () {
        QueryToolbox.rename($(this).val());
    });




    // *** VARIABLE FIELDS - GROUPBY - ORDERING - RESOLUTIONS *** //
    /* On variable remove */
    $('body').on('click', '.value-remove-btn', function () {
        // mark as unsaved
        QueryToolbox.tabMarker.currentUnsaved();
        QueryToolbox.removeVariableField($(this).closest('.fieldset'));
        $(".fieldset").each(function (idx, elem) {
            $(elem).find('.metric-cnt').text(String(idx+1));
        });

        var variable_id = $(this).closest('.fieldset').find('[name="variable_field"]').data('variable-id');
        $.each(QueryToolbox.variables, function (idx, variable) {
            if(parseInt(variable_id) === parseInt(variable.id)){
                QueryToolbox.variables.splice(idx, 1);
                return false; // break
            }
        });
        updateQDfields();
    });

    /* On spatial resolution field change */
    $('body').on('change', '#spatial_resolution', function (e) {
        // update spatial resolution
        QueryToolbox.spatial_resolution = $("#spatial_resolution").val();
        // if spatial resolution is defined
        if($("#spatial_resolution").val() !== ''){
            // Each variable should have an aggregation function
            $("select[name='field_aggregate']").each(function () {
                $(this).val("AVG");
                $(this).trigger("change");
            });
            // Disable the 'no-aggregate' option
            $("select[name='field_aggregate']").find('option[value=""]').each(function () {
                $(this).attr('disabled', 'disabled');
            });
        }
        // if spatial resolution is NOT defined
        else{
            // check if spatial resolution is defined
            if ($("#temporal_resolution").val() === "") {
                // check if group-by is defined and either reset or not the aggregate values
                if ($('[name="category"]').val().length === 0) {
                    $("select[name='field_aggregate']").find('option[value=""]').each(function () {
                        $(this).attr('disabled', false);
                    });
                    $("select[name='field_aggregate']").each(function () {
                        $(this).val("");
                        $(this).trigger("change");
                    });
                }
            }
        }
        // mark as unsaved
        QueryToolbox.tabMarker.currentUnsaved();
    });

    /* On temporal resolution field change */
    $('body').on('change', '#temporal_resolution', function (e) {
        // update temporal resolution
        QueryToolbox.temporal_resolution = $("#temporal_resolution").val();

        if($("#temporal_resolution").val() !== ''){
            // Each variable should have an aggregation function
            $("select[name='field_aggregate']").each(function () {
                $(this).val("AVG");
                $(this).trigger("change");
            });
            // Disable the 'no-aggregate' option
            $("select[name='field_aggregate']").find('option[value=""]').each(function () {
                $(this).attr('disabled', 'disabled');
            });
        }
        else{
            // check if spatial resolution is defined
            if ($("#spatial_resolution").val() === "") {
                // check if group-by is defined and either reset or not the aggregate values
                if ($('[name="category"]').val().length === 0) {
                    $("select[name='field_aggregate']").find('option[value=""]').each(function () {
                        $(this).attr('disabled', false);
                    });
                    $("select[name='field_aggregate']").each(function () {
                        $(this).val("");
                        $(this).trigger("change");
                    });
                }
            }
        }
        $("select[name='field_aggregate']").select2();
        // mark as unsaved
        QueryToolbox.tabMarker.currentUnsaved();
    });

    /* On groupby field change */
    $('body').on('change', 'select[name="category"]', function (e) {
        QueryToolbox.groupings = [];
        // The groupby select field
        var $categorySelectField = $('[name="category"]');
        // The already selected values
        var $selected_options = $categorySelectField.find("option:selected");
        $.each($selected_options, function (_, option) {
            QueryToolbox.groupings.push(
                {'dimension_id': $(option).data('dimension-id'),
                 'dimension_title': $(option).data('title'),
                 'dimension_forVariable': $(option).data('forvariable')
                })
        });

        // if a group by column is selected, put the AVG as the default aggr function to all variables
        if($("select[name='category']").val().length > 0){
            // Each variable should have an aggregation function
            $("select[name='field_aggregate']").each(function () {
                $(this).val("AVG");
                $(this).trigger("change");
            });
            // Disable the 'no-aggregate' option
            $("select[name='field_aggregate']").find('option[value=""]').each(function () {
                $(this).attr('disabled', 'disabled');
            });
        }
        else{
            // check if spatial resolution is defined
            if ($("#spatial_resolution").val() === "") {
                // check if temporal resolution is defined
                if ($("#temporal_resolution").val() === "") {
                    $("select[name='field_aggregate']").find('option[value=""]').each(function () {
                        $(this).attr('disabled', false);
                    });
                    $("select[name='field_aggregate']").each(function () {
                        $(this).val("");
                        $(this).trigger("change");
                    });
                }
            }
        }
        // mark as unsaved
        QueryToolbox.tabMarker.currentUnsaved();
    });

    /* On ordering field change */
    $('body').on('change', 'select[name="orderby"]', function (e) {
        QueryToolbox.orderings = [];
        // The ordering select field
        var $orderingSelectField = $('[name="orderby"]');
        // The already selected values
        var $selected_options = $orderingSelectField.find("option:selected");

        // Disable the opposite ordering types
        $orderingSelectField.find("option").attr('disabled', false);
        $.each($selected_options, function (_, opt) {
            var ordering = $(opt).data("ordering");
            var column_type = $(opt).data("type");
            if(column_type === 'dimension'){
                var dimension_id = $(opt).data("dimension-id");
                $orderingSelectField.find("option").filter("[data-dimension-id='"+dimension_id+"']").not("[data-ordering='"+ordering+"']").attr('disabled', 'disabled');
            }
            if(column_type === 'variable'){
                var variable_id = $(opt).data("variable-id");
                $orderingSelectField.find("option").filter("[data-variable-id='"+variable_id+"']").not("[data-ordering='"+ordering+"']").attr('disabled', 'disabled');
            }
        });
        // $orderingSelectField.select2();
        // $orderingSelectField.select2({
            // width: "100%",
            // escapeMarkup: function(markup) {
            //     return markup;
            // }
        // });


        $.each($selected_options, function (_, option) {
            if($(option).data('type') === 'dimension'){
                QueryToolbox.orderings.push(
                    {'dimension_id': $(option).data('dimension-id'),
                     'title': $(option).data('title'),
                     'dimension_forVariable': $(option).data('forvariable'),
                     'ordering': $(option).data('ordering'),
                     'type': 'dimension'
                    }
                )
            }
            else{
                QueryToolbox.orderings.push(
                    {'variable_id': $(option).data('variable-id'),
                     'title': $(option).data('title'),
                     'ordering': $(option).data('ordering'),
                     'type': 'variable'
                    }
                )
            }
        });
        // mark as unsaved
        QueryToolbox.tabMarker.currentUnsaved();
    });

    /* On aggregate change */
    $('body').on('change', 'select[name="field_aggregate"]', function () {
        var aggr = $(this).val();
        var $variable_field = $(this).closest('.fieldset').find('[name="variable_field"]');
        $.each(QueryToolbox.variables, function (_, variable) {
            if(parseInt(variable.id) === parseInt($variable_field.data('variable-id'))){
                variable.aggregate = aggr;
            }
        });
        $(this).select2();
        // mark as unsaved
        QueryToolbox.tabMarker.currentUnsaved();
    });




    // *** FILTERS *** //
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
    });

    /* On filter expression type change */
    $('body').on('change', '#filters-expr-type', function () {
        // mark as unsaved
        QueryToolbox.tabMarker.currentUnsaved();
        QueryToolbox.filterManager.setExpressionType($(this).val());
    });

    /* On filter remove */
    $('body').on('click', '.remove-filter-btn', function () {
        // mark as unsaved
        QueryToolbox.tabMarker.currentUnsaved();
        QueryToolbox.filterManager.removeFilter($(this).closest('tr').find('> td:first-of-type').text());
    });




    // *** RUN QUERY / EXPLORE RESULTS *** //
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




    // *** SHOW VARIABLE DIMENSIONS *** //
    $('body').on('click', '.fieldset input[readonly]', function () {
        $(this).closest('.fieldset').find('.collapse').collapse("toggle");
    });

});


function updateQDfields() {
    updateGroupByField();
    updateOrderByField();
    updateFilterByField();
}


function updateGroupByField() {
    // The groupby select field
    var $categorySelectField = $('[name="category"]');

    // Empty the field to re-enter the options
    $categorySelectField.find("option").remove();
    $categorySelectField.val('');

    $.each(QueryToolbox.variables, function (_, variable) {
        $.each(variable.dimensions, function (_, dimension) {
            if ($categorySelectField.find("option[data-title='" + dimension.title + "']").length === 0) {
                // Create a DOM Option and pre-select by default
                var newOption = new Option(dimension.title, dimension.id, false, false);
                newOption.setAttribute('data-forVariable', variable.id);
                newOption.setAttribute('data-dimension-id', dimension.id);
                newOption.setAttribute('data-title', dimension.title);
                // if a dimensions was previously selected, then select it again
                $.each(QueryToolbox.groupings, function (idx, elem) {
                    if(elem.dimension_title === dimension.title){
                        newOption.setAttribute('selected','selected');
                    }
                });
                // Append it to the select
                $categorySelectField.append(newOption);
            }
        })
    });
    $categorySelectField.trigger('change');
}

function updateOrderByField() {
    // The orderby select field
    var $orderbySelectField = $('[name="orderby"]');

    // Empty the field to re-enter the options
    $orderbySelectField.find("option").remove();
    $orderbySelectField.val('');

    $.each(QueryToolbox.variables, function (idx, variable) {
        $.each(variable.dimensions, function (_, dimension) {
            // Append the dimensions
            if ($orderbySelectField.find("option[data-title='" + dimension.title + "']").length === 0) {
                //Ascending order
                var newOption = new Option('<i class="fa fa-arrow-up"></i> ' + dimension.title, 'dimension__'+dimension.id+'__ASC', false, false);
                newOption.setAttribute('data-forVariable', variable.id);
                newOption.setAttribute('data-dimension-id', dimension.id);
                newOption.setAttribute('data-ordering', 'ASC');
                newOption.setAttribute('data-title', dimension.title);
                newOption.setAttribute('data-type', 'dimension');
                // if a dimensions was previously selected, then select it again
                $.each(QueryToolbox.orderings, function (idx, elem) {
                    if((elem.type === 'dimension') && (elem.title === dimension.title) && (elem.ordering === 'ASC')){
                        newOption.setAttribute('selected','selected');
                    }
                });
                $orderbySelectField.append(newOption);
                //Descending order
                newOption = new Option('<i class="fa fa-arrow-down"></i> ' + dimension.title, 'dimension__'+dimension.id+'__DESC', false, false);
                newOption.setAttribute('data-forVariable', variable.id);
                newOption.setAttribute('data-dimension-id', dimension.id);
                newOption.setAttribute('data-ordering', 'DESC');
                newOption.setAttribute('data-title', dimension.title);
                newOption.setAttribute('data-type', 'dimension');
                // if a dimensions was previously selected, then select it again
                $.each(QueryToolbox.orderings, function (idx, elem) {
                    if((elem.type === 'dimension') && (elem.title === dimension.title) && (elem.ordering === 'DESC')){
                        newOption.setAttribute('selected','selected');
                    }
                });
                $orderbySelectField.append(newOption);
            }
        });
        // Append the variable, too
        //Ascending order
        var newOption = new Option('<i class="fa fa-arrow-up"></i> ' + variable.title + ' (Metric #'+(idx+1)+')', 'variable__'+variable.id+'__ASC', false, false);
        newOption.setAttribute('data-variable-id', variable.id);
        newOption.setAttribute('data-ordering', 'ASC');
        newOption.setAttribute('data-title', variable.title);
        newOption.setAttribute('data-type', 'variable');
        // if the variable was previously selected, then select it again
        $.each(QueryToolbox.orderings, function (idx, elem) {
            if((elem.type === 'variable') && (parseInt(elem.variable_id) === parseInt(variable.id)) && (elem.ordering === 'ASC')){
                newOption.setAttribute('selected','selected');
            }
        });
        $orderbySelectField.append(newOption);
        //Descending order
        newOption = new Option('<i class="fa fa-arrow-down"></i> ' + variable.title + ' (Metric #'+(idx+1)+')', 'variable__'+variable.id+'__DESC', false, false);
        newOption.setAttribute('data-variable-id', variable.id);
        newOption.setAttribute('data-ordering', 'DESC');
        newOption.setAttribute('data-title', variable.title);
        newOption.setAttribute('data-type', 'variable');
        // if the variable was previously selected, then select it again
        $.each(QueryToolbox.orderings, function (idx, elem) {
            if((elem.type === 'variable') && (parseInt(elem.variable_id) === parseInt(variable.id)) && (elem.ordering === 'DESC')){
                newOption.setAttribute('selected','selected');
            }
        });
        $orderbySelectField.append(newOption);
    });
    $orderbySelectField.trigger('change');
}

function updateFilterByField(){
    var $filterSelectField = $('#new-filter-variable');

    // Empty the field to re-enter the options
    $filterSelectField.find("option").remove();
    $filterSelectField.val('');


    $.each(QueryToolbox.variables, function (idx, variable) {
        $.each(variable.dimensions, function (_, dimension) {
            if ($filterSelectField.find("option[data-title='" + dimension.title + "']").length === 0) {
                if((dimension.title !== 'time') && (dimension.title !== 'latitude') && (dimension.title !== 'longitude')) {
                    var newOption = new Option(dimension.title, 'dimension__' + dimension.id, false, false);
                    newOption.setAttribute('data-forvariable', variable.id);
                    newOption.setAttribute('data-id', dimension.id);
                    newOption.setAttribute('data-title', dimension.title);
                    newOption.setAttribute('data-type', 'dimension');
                    $filterSelectField.append(newOption);
                }
            }
        });
        // Append the variable, too
        var newOption = new Option(variable.title + ' (Metric #'+(idx+1)+')', 'variable__'+variable.id, false, false);
        newOption.setAttribute('data-id', variable.id);
        newOption.setAttribute('data-title', variable.title);
        newOption.setAttribute('data-type', 'variable');
        newOption.setAttribute('data-forvariable', variable.id);
        $filterSelectField.append(newOption);
    });
    $filterSelectField.trigger('change');

    // if a filter was previously defined, then define it again
    updateSelectedFilters();
}

function updateSelectedFilters(){
    var updated_filters = [];

    $.each(Object.keys(QueryToolbox.filters), function (fidx, fkey) {
        var found = false;
        var filter = QueryToolbox.filters[fkey];
        $.each(QueryToolbox.variables, function (vidx, variable) {
            // Is it a dimension filter?
            if ((filter.a_type === "dimension") && (found === false)) {
                $.each(variable.dimensions, function (didx, dimension) {
                    if (filter.a_title === dimension.title) {
                        filter.a = dimension.id;
                        filter.a_forVariable = variable.id;
                        updated_filters[fkey] = filter;
                        found = true;
                    }
                })
            }
            if ((filter.a_type === "variable") && (parseInt(filter.a) === parseInt(variable.id))) {
                updated_filters[fkey] = filter;
            }
        })
    });

    QueryToolbox.filters = updated_filters;
    $(".filter-counter").text(Object.keys(QueryToolbox.filters).length);
}