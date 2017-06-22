/**
 * Created by dimitris on 21/6/2017.
 */
$(function() {
    /* On change show/hide base services */
    $('.home-search-form input').on('keyup', function() {
        var term = $(this).val().toLowerCase();

        $.each($('.service-tile'), function(idx, tile) {
            var $tile = $(tile);

            if (($tile.find('.title').text().toLowerCase().indexOf(term) >= 0) ||
                    ($tile.find('.moto').text().toLowerCase().indexOf(term) >= 0)) {
                $tile.removeClass('hidden')
            } else {
                $tile.addClass('hidden')
            }
        });
    })
});