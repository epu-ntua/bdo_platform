$(function() {

    // *** DATA SELECTION MODAL *** //
    /* Open the data selection modal to add variables */
    $('body').on('click', '.add-value-field', function () {
        $('#select-data-modal').dialog({
            width: '60vw',
            position: {my: 'center'},
            title: 'Select data'
        });
    });

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
        var label = 'Variable #<span class="metric-cnt">' + ($chartControls.find('> *').length ) + '</span>';
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
        console.log(QueryToolbox.variables);

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
        updateQDfields();
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
    });

    /* On groupby field change */
    $('body').on('change', 'select[name="category"]', function (e) {
        // if a group by column is selected, put the AVG as the default aggr function to all variables
        if($("select[name='category']").val().length > 0){
            $("select[name='field_aggregate']").each(function () {
                $(this).val("AVG");
                $(this).trigger("change");
            });
        }
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

    // The already selected values
    var selected_values = $categorySelectField.val();

    $.each(QueryToolbox.variables, function (_, variable) {
        $.each(variable.dimensions, function (_, dimension) {
            if ($categorySelectField.find("option[data-title='" + dimension.title + "']").length === 0) {
                // Create a DOM Option and pre-select by default
                var newOption = new Option(dimension.title, dimension.id, false, false);
                newOption.setAttribute('data-forVariable', variable.id);
                newOption.setAttribute('data-dimension-id', dimension.id);
                newOption.setAttribute('data-title', dimension.title);
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
    $.each(QueryToolbox.variables, function (_, variable) {
        $.each(variable.dimensions, function (_, dimension) {
            if ($orderbySelectField.find("option[data-title='" + dimension.title + "']").length === 0) {
                //Ascending order
                var newOption = new Option(dimension.title + ' - ASC', dimension.id, false, false);
                newOption.setAttribute('data-forVariable', variable.id);
                newOption.setAttribute('data-dimension-id', dimension.id);
                newOption.setAttribute('data-ordering', 'ASC');
                newOption.setAttribute('data-title', dimension.title);
                $orderbySelectField.append(newOption);
                //Descending order
                newOption = new Option(dimension.title + ' - DESC', dimension.id, false, false);
                newOption.setAttribute('data-forVariable', variable.id);
                newOption.setAttribute('data-dimension-id', dimension.id);
                newOption.setAttribute('data-ordering', 'DESC');
                newOption.setAttribute('data-title', dimension.title);
                $orderbySelectField.append(newOption);
            }
        })
    });
    $orderbySelectField.trigger('change');
}

function updateFilterByField(){
    var $filterSelectField = $('#new-filter-variable');
    $.each(QueryToolbox.variables, function (_, variable) {
        $.each(variable.dimensions, function (_, dimension) {
            if ($filterSelectField.find("option[data-title='" + dimension.title + "']").length === 0) {
                var newOption = new Option(dimension.title, dimension.id, false, false);
                newOption.setAttribute('data-forVariable', variable.id);
                newOption.setAttribute('data-dimension-id', dimension.id);
                newOption.setAttribute('data-title', dimension.title);
                $filterSelectField.append(newOption);
            }
        })
        // TODO: ADD THE VARIABLES TOO
    });
    $filterSelectField.trigger('change');

    QueryToolbox.filterManager.updateFilters(QueryToolbox._getChartInfo().values);
}