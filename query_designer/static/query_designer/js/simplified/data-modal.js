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

    /* select variable */
    window.getDataSelection = function() {
        let dims = [];
        $('#group-by-select option').each(function () {
            dims.push({
                value: $(this).val(),
                title: $(this).text().split(',')[0]
            })
        });

        let datasetInfoDivElem = $('.dataset1_info_div');
        return {
            value: datasetInfoDivElem.find('.variable-section.selected').find('.variable-name').text(),
            title: datasetInfoDivElem.find('.variable-section.selected').find('.variable-title').text(),
            id: datasetInfoDivElem.find('.variable-section.selected').find('.variable-id').text(),
            unit: datasetInfoDivElem.find('.variable-section.selected').find('.variable-unit').text(),
            aggregate: $('#selection-aggregate').val(),
            groupBy: $('#group-by-select').val(),
            dimensions: dims
        }
    };

    $(".dataset-metadata-btn").click(function () {
        $(this).parent().parent().find('.dataset-metadata').collapse("toggle");
    });


     $(".dataset-title").click(function () {
         let $dataset1InfoDiv = $('.dataset1_info_div');
         $dataset1InfoDiv.find(".dataset-info").remove();
        // $(this).clone().appendTo('.dataset1_info_div');
        $(this).parent().parent().clone().appendTo('.dataset1_info_div');
        $dataset1InfoDiv.get(0).classList.remove('collapse');
         $dataset1InfoDiv.find(".dataset-info").find(".variables1").show();
         $dataset1InfoDiv.find(".dataset-info").find(".dataset-name").find(".dimensions").show();
    });

   $('.dataset1_info_div').on('click', ".variable-title", function() {

       $modal.find('.variable-section').removeClass('selected');
        $(this).parent().parent().addClass('selected');

       let $selectionCol = $('.selection-confirm > div');
       $selectionCol.removeClass('hidden');
        // $selectionCol.find('#selection-aggregate').val('AVG').trigger('change');
        $selectionCol.find('#selection-aggregate').val(null).trigger('change');


        // remove old group by
        $('#group-by-select').remove();

        // add group by options
        var $gSelect = $('<select />')
            .attr('id', 'group-by-select')
            .attr('multiple', 'multiple');

        $.each($(this).parent().parent().find('.dimensions > span'), function(idx, dimension) {
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
});