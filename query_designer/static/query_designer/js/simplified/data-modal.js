$(function() {
    var $modal = $('#select-data-modal');

    /* Autocomplete */
    $modal.find('#data-filter-search').on('keyup', function() {
        var term = $(this).val().toLowerCase();

        // hide/show variables
        $.each($modal.find('.variable-section'), function(idx, section) {
            var $section = $(section);

            if ($section.text().toLowerCase().indexOf(term) >= 0) {
                $section.removeClass('hidden')
            } else {
                $section.addClass('hidden')
            }
        });

        // hide-show datasets
        $.each($modal.find('.dataset-section'), function(idx, section) {
            var $section = $(section);

            if ($section.find('.variable-section').length === $section.find('.variable-section.hidden').length) {
                $section.addClass('hidden')
            } else {
                $section.removeClass('hidden')
            }
        });

        // hide-show no results
        if ($modal.find('.variable-section:not(.hidden)').length === 0) {
            $modal.find('.no-results').removeClass('hidden')
        } else {
            $modal.find('.no-results').addClass('hidden')
        }
    });

    /* Select variable */
    $modal.find('.variable-section').on('click', function() {
        $modal.find('.variable-section').removeClass('selected');
        $(this).addClass('selected');

        var $selectionCol = $modal.find('.selection-confirm > div');
        $selectionCol.removeClass('hidden');
        // $selectionCol.find('#selection-aggregate').val('AVG');
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
            unit: $modal.find('.variable-section.selected').find('.variable-unit').text(),
            aggregate: $modal.find('#selection-aggregate').val(),
            groupBy: $modal.find('#group-by-select').val(),
            dimensions: dims
        }
    };
    
    $(".dataset-metadata-btn").click(function () {
        $(this).parent().parent().find('.dataset-metadata').collapse("toggle");
    })
});