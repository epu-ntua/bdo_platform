/**
 * Created by dimitris on 12/5/2017.
 */
QueryExecutor = function(qd) {
    var that = this;

    this.qd = qd;

    this.ui = {
        $elem: undefined,

        render: function() {

        }
    };

    this.run = function() {
        var config = that.qd.config.endpoint,
            requestParameters = jQuery.extend(true, {}, config.defaultParameters);

        // add query property
        requestParameters[config.queryParameter] = that.qd.workbench.query;

        $.ajax({
            'url': config.url,
            'type': config.type,
            'data': requestParameters,
            success: function(data) {
                console.log(data);
            }
        })
    };

    this.ui.render();

    /* F9 to run query */
	$("body").on('keyup', function(e) {
	    if (e.keyCode == 120) { // F9 key pressed
            that.run();
        }
    });

    return this;
};