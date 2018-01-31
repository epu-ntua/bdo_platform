    $(function() {
        /* Data tables init */
        $('table').DataTable({
            bLengthChange: false,
            language: {
                emptyTable: gettext('No charts available'),
                zeroRecords: gettext('No charts found')
            }
        });

        /* On click chart row */
        $('body').on('click', 'tr.full-chart-row[data-href]', function(e) {
            document.location = $(this).data('href');
        });

        /* On click chart delete button */
        $('body').on('click', '.delete-chart', function(e) {
            // don't follow the link
            e.preventDefault();
            e.stopPropagation();

            var $chartContainer = $(this).closest('.chart-open-teaser');
            if ($chartContainer.length == 0) {
                $chartContainer = $(this).closest('.full-chart-row')
            }

            var chartName = $chartContainer.find('.chart-title').text();
            $('#chart-delete-modal').find('.modal-body').text(gettext('Are you sure you want to delete chart') + ' «' + chartName + '»?');
            $('#chart-delete-modal').modal('show');

            // set the chart id to remove
            var chartId = $chartContainer.data('chart_id');
            $('#chart-delete-modal').data('chart_id', chartId);
            $('#chart-delete-modal').attr('data-chart_id', chartId);
        });

        /* On click "Yes" in the chart delete dialog */
        $('body').on('click', '#chart-delete-modal .perform-chart-delete', function(e) {
            // get the id to delete
            var chartId = $('#chart-delete-modal').data('chart_id');

            // hide from the list
            var $teaser = $('.chart-open-teaser[data-chart_id="' + chartId + '"]');
            $teaser.closest('.chart-col').hide();
            var $teaserRow = $('tr.full-chart-row[data-chart_id="' + chartId + '"]');
            $teaserRow.hide();

            // hide the modal
            $('#chart-delete-modal').modal('hide');

            // send the delete request
            $.ajax({
                url: '/chart/' + chartId + '/delete/',
                type: 'POST',
                data: {
                    'csrfmiddlewaretoken': $('#chart-delete-modal input[name="csrfmiddlewaretoken"]').val()
                },
                success: function(data) {
                    $teaser.remove();
                    $teaserRow.remove();
                },
                error: function(xhr, status, error) {
                    $teaser.closest('.chart-col').show();
                    $teaserRow.show();
                    alert(gettext('An error occurred, please try again later'));
                }
            });
        });
    });