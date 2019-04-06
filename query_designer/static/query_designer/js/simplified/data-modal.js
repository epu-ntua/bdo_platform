$(function() {
    var $modal = $('#select-data-modal');

     $(".dataset-section").click(function () {
         // Update the selection
         $(".dataset-section").not(this).attr("data-selected", "False");
         $(this).attr("data-selected", "True");

         var $datasetInfoDiv = $('#dataset_info_div');
         // Empty the previous info
         $datasetInfoDiv.find("#dataset_basic_info_div").empty();
         $datasetInfoDiv.find("#dataset-variables-div").empty();
         $datasetInfoDiv.find("#dataset-dimensions-div").empty();
         $datasetInfoDiv.find("#dataset-coverage-div").empty();
         $datasetInfoDiv.find("#dataset_metadata_div").empty();
         // Append the new dataset info
         $(this).find('.dataset-info .dataset-metadata').clone().appendTo($datasetInfoDiv.find("#dataset_metadata_div"));
         $(this).find('.dataset-info .dataset-variables-div').clone().appendTo($datasetInfoDiv.find("#dataset-variables-div"));
         $(this).find('.dataset-info .dataset-dimensions-div').clone().appendTo($datasetInfoDiv.find("#dataset-dimensions-div"));
         $(this).find('.dataset-info .dataset-coverage-div').clone().appendTo($datasetInfoDiv.find("#dataset-coverage-div"));
         $(this).find('.dataset-name').clone().appendTo($datasetInfoDiv.find("#dataset_basic_info_div"));

         $datasetInfoDiv.removeClass("hidden");

         // Mark as selected the variables that are already added to the Query Designer
         var included_vars = [];
         $.each(QueryToolbox.variables, function (_, variable) {
             included_vars.push(parseInt(variable.id));
         });
         $("#dataset-variables-div .variable-section").each(function (_, variable) {
             if(included_vars.indexOf($(variable).data('variable-id')) >= 0){
                 $(variable).attr({'data-selected': 'True'});
                 $(variable).attr({'data-disabled': 'True'});
             }
             else{
                 $(variable).attr({'data-selected': 'False'});
                 $(variable).attr({'data-disabled': 'False'});
             }
        });
    });

   $('#dataset_info_div').on('click', ".variable-section[data-disabled='False']", function() {
       /* Select/Unselect variable */
       if($(this).attr('data-selected') === "False") {
           $(this).attr({'data-selected': 'True'});
       }
       else{
           $(this).attr({'data-selected': 'False'});
       }
       $(this).attr({'data-disabled': 'False'});

       if($("#dataset-variables-div .variable-section[data-selected='True']").length > 0 ) {
           $('.selection-confirm').show();
       }
       else{
           $('.selection-confirm').hide();
       }

       window.getDataSelection = function() {
           var selection = [];
           $("#dataset-variables-div .variable-section[data-selected='True']").each(function (_, variable) {
               // Gather the dimensions of the selected variable
               var dims = [];
               $(this).find(".dimension-section span").each(function (_, dim) {
                   dims.push({
                        id: $(dim).data('type'),
                        title: $(this).data('name'),
                        datatype: $(this).data('datatype')
                    })
               });
               selection.push({
                    id: $(variable).data('variable-id'),
                    name: $(variable).data('variable-name'),
                    title: $(variable).data('variable-title'),
                    unit: $(variable).data('variable-unit'),
                    datatype: $(variable).data('variable-datatype'),
                    dataset_id: $(variable).data('variable-dataset'),
                    dataset_size: $(variable).closest('#dataset_info_div').find("#dataset_metadata_div").find(".dataset-size").find("td").eq(1).text(),
                    dataset_name: $(variable).closest('#dataset_info_div').find("#dataset_basic_info_div").find(".dataset-title").text(),
                    aggregate: null,
                    groupBy: null,
                    dimensions: dims
                })
           });
           // console.log(selection);
           return selection;
       };
   });


    $(".jplist-reset-btn").click(function(){
        setTimeout(function(){$('#dataset-filter-section select').trigger("change");}, 100);
    });
});