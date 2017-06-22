/**
 * Created by dimitris on 22/6/2017.
 */
$(function() {
    /* Temporarily using long polling, we'll switch to sockets */
    var checkAndPoll = function() {
        var $jobContainer = $('#job-analysis--details'),
            status = $jobContainer.find('.status-cell').data('status');

        if (['FINISHED', 'FAILED'].indexOf(status) >= 0) {
            $('#email-notify-checkbox').remove();
            return
        }

        setTimeout(function() {
            $.ajax({
                url: document.location.pathname,
                type: 'GET',
                data: {partial: 'true'},
                success: function(resp) {
                    $jobContainer.html(resp);
                    checkAndPoll();
                }
            })
        }, 2000);
    };

    // start polling
    checkAndPoll();
});