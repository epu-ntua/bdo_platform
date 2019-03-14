$(function() {
    var $modal = $('#select-data-modal');

    /* Select variable */
    $modal.find('.variable-section').on('click', function() {
        $modal.find('.variable-section').removeClass('selected');
        $(this).addClass('selected');

        // Display the selection div at the bottom of the modal
        var $selectionConfirmPanel = $modal.find('.selection-confirm > div');
        $selectionConfirmPanel.removeClass('hidden');
        // Reset the aggregate select
        $selectionConfirmPanel.find('#selection-aggregate').val(null).trigger('change');
        // Reset the  group by select
        var $gSelect = $selectionConfirmPanel.find('#group-by-select');
        $gSelect.empty();
        $gSelect.val(null).trigger('change');

        // Add only the dimensions as groupby options
        $.each($(this).find('.dimensions > span'), function(idx, dimension) {
            var $dimension = $(dimension);
            // For each option: value=pk of dimension, text=title of dimension
            var $opt = $('<option />')
                .attr('value', $dimension.data('type'))
                .text($dimension.text());
            $gSelect.append($opt);
        });
        $gSelect.val(null).trigger('change');
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
    
    $(".dataset-metadata-btn").click(function () {
        $(this).parent().parent().find('.dataset-metadata').collapse("toggle");
    });
     $(".dataset-title").click(function () {
        $(this).closest(".dataset-section").find('.dataset_collapse_div').collapse("toggle");
    });
});