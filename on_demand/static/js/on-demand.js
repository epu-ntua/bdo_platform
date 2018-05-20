$(function() {
    /* Mark as accepted */
    $('.on-demand--reply .btn-accept-response').on('click', function() {
        var $this = $(this);

        if ($this.attr('disabled')) {
            return
        }

        $this.attr('disabled', 'disabled');
        $this.text('Accepting...');

        var requestId = $this.data('requestid');
        var replyId = $this.data('replyid');

        $.ajax({
            url: '/on-demand/' + requestId + '/accept/' + replyId + '/',
            type: 'POST',
            data: {
                csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val()
            },
            success: function(){
                // just refresh
                window.location.reload();
            },
            error: function() {
                alert('An error occurred, please try again later.')
            }
        });
    });

    /* Upvote & cancel */
    $('.on-demand--upvote').on('click', function() {
        var $this = $(this);

        if ($this.attr('disabled')) {
            return
        }

        $this.attr('disabled', 'disabled');

        var requestId = $this.data('requestid');
        var nUpvotes = Number($this.find('.count').text());
        var hasUpvoted = $this.hasClass('upvoted');

        if (!hasUpvoted) {
            $.ajax({
                url: '/on-demand/' + requestId + '/upvote/',
                type: 'POST',
                data: {
                    csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val()
                },
                success: function(){
                    // update count, title & class
                    $this.find('.count').text(nUpvotes + 1);
                    $this.addClass('upvoted');
                    $this.attr('Title', 'Remove upvote');

                    // enable again
                    $this.removeAttr('disabled');
                },
                error: function() {
                    alert('An error occurred, please try again later.')
                }
            });
        } else {
            $.ajax({
                url: '/on-demand/' + requestId + '/upvote/',
                type: 'DELETE',
                beforeSend: function(xhr) {
                    xhr.setRequestHeader("X-CSRFToken", $('input[name="csrfmiddlewaretoken"]').val());
                },
                success: function(){
                    // update count, title & class
                    $this.find('.count').text(nUpvotes - 1);
                    $this.removeClass('upvoted');
                    $this.attr('Title', 'Click to upvote');

                    // enable again
                    $this.removeAttr('disabled');
                },
                error: function() {
                    alert('An error occurred, please try again later.')
                }
            });
        }
    });
});