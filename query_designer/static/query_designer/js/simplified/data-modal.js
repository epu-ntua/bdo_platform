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
         // Append the new dataset info
         // console.log($(this).find('.dataset-info'));
         // console.log($(this).find($datasetInfoDiv));
         $(this).find('.dataset-info .dataset-metadata').clone().appendTo($datasetInfoDiv.find("#dataset_basic_info_div"));
         $(this).find('.dataset-info .dataset-variables-div').clone().appendTo($datasetInfoDiv.find("#dataset-variables-div"));
         $(this).find('.dataset-info .dataset-dimensions-div').clone().appendTo($datasetInfoDiv.find("#dataset-dimensions-div"));

         $datasetInfoDiv.removeClass("hidden");
    });

   $('.dataset1_info_div').on('click', ".variable-title", function() {

       $modal.find('.variable-section').removeClass('hidden');
       /* Select variable */
       $modal.find('.variable-section').on('click', function () {
           $modal.find('.variable-section').removeClass('hidden');
           $(this).addClass('selected');

           var $selectionCol = $('.selection-confirm > div');
           $selectionCol.removeClass('hidden');
           // $selectionCol.find('#selection-aggregate').val('AVG').trigger('change');
           $selectionCol.find('#selection-aggregate').val(null).trigger('change');


           // remove old group by
           $('#group-by-select').remove();

           // add group by options
           var $gSelect = $('<select />')
               .attr('id', 'group-by-select')
               .attr('multiple', 'multiple');

           $.each($(this).parent().parent().find('.dimensions > span'), function (idx, dimension) {
               var $dimension = $(dimension);

               var $opt = $('<option />')
                   .attr('value', $dimension.data('type'))
                   .text($dimension.text());

               if ($dimension.text().toLowerCase().indexOf('time') >= 0) {
                   $opt.attr('selected', 'selected');
               }

               $gSelect.append($opt);
           });

           // add & config plugin
           $('.selection-group-by').append($gSelect);
           $("#group-by-select").val(null).trigger('change');
           $gSelect.select2();
       });

       window.getDataSelection = function() {
            // Gather the dimensions of the selected variable
            var dims = [];
            $modal.find('.variable-section.selected').find('.dimensions span').each(function () {
                dims.push({
                    id: $(this).data('type'),
                    title: $(this).data('name')
                })
            });
            return {
                id: $modal.find('.variable-section.selected').find('.variable-id').text(),
                name: $modal.find('.variable-section.selected').find('.variable-name').text(),
                title: $modal.find('.variable-section.selected').find('.variable-title').text(),
                unit: $modal.find('.variable-section.selected').find('.variable-unit').text(),
                aggregate: $modal.find('#selection-aggregate').val(),
                groupBy: $modal.find('#group-by-select').val(),
                dimensions: dims
            }
        };
   })
});