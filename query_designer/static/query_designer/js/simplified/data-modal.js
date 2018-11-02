$(function() {
    var $modal = $('#select-data-modal');

    /* Select variable */
    $modal.find('.variable-section').on('click', function() {
        $modal.find('.variable-section').removeClass('selected');
        $(this).addClass('selected');

        var $selectionCol = $modal.find('.selection-confirm > div');
        $selectionCol.removeClass('hidden');
        // $selectionCol.find('#selection-aggregate').val('AVG').trigger('change');
        $selectionCol.find('#selection-aggregate').val(null).trigger('change');


        // remove old group by
        $modal.find('#group-by-select').remove();

        // add group by options
        var $gSelect = $('<select />')
            .attr('id', 'group-by-select')
            .attr('multiple', 'multiple');

        $.each($(this).find('.dimensions > span'), function(idx, dimension) {
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
        $modal.find('.selection-group-by').append($gSelect);
        $("#group-by-select").val(null).trigger('change');
        $gSelect.select2();
    });

    window.getDataSelection = function() {
        var dims = [];
        $('#group-by-select option').each(function () {
            dims.push({
                value: $(this).val(),
                title: $(this).text().split(',')[0]
            })
        });
        return {
            value: $modal.find('.variable-section.selected').find('.variable-name').text(),
            title: $modal.find('.variable-section.selected').find('.variable-title').text(),
            id: $modal.find('.variable-section.selected').find('.variable-id').text(),
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