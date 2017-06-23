/**
 * Created by dimitris on 23/6/2017.
 */
QueryStorage = function(qd, pk) {
    var that = this;

    this.qd = qd;
    this.pk = pk;

    this.load = function() {
        $.ajax({
            url: '/queries/load/' + pk + '/',
            type: 'GET',
            success: function(qObj) {
                that.pk = qObj.pk;
                that.title = qObj.title;
                qd.workbench.builder.fromJson(qObj.design);
            }
        })
    };

    this.save = function(title) {
        var postEndpoint = "/queries/save/";
        if (pk !== undefined) {
            postEndpoint += pk + '/'
        }

        // console.log(qd.workbench)
        var data = {
            title: title,
            document: JSON.stringify(new DocumentBuilder(that.qd).getDocument()),
            design: JSON.stringify(qd.workbench.builder.toJson())
        };

        $.ajax({
            url: postEndpoint,
            type: "POST",
            data: data,
            success: function (qObj) {
                $("#alert_modal .modal-title").html('LinDA Queries');
                $("#alert_modal .modal-body").html('Query saved');
                $("#alert_modal .modal-footer .btn-default").html('Close');
                $("#alert_modal").show();

                if (typeof(that.qd.builder) !== "undefined") {
                    that.qd.builder.saved_query = that.qd.builder.query;
                }

                // store PK
                that.pk = pk;

                // query title
                $('.designer-menu .query-title').html('#' + qObj.pk + ': ' + qObj.title);
            },
            error: function (jqXHR) {
                $("#alert_modal .modal-title").html('Error');
                $("#alert_modal .modal-body").html(jqXHR.responseText);
                $("#alert_modal .modal-footer .btn-default").html('OK');
                $("#alert_modal").show();
            }
        });
    };

    if (this.pk !== undefined) {
        setTimeout(this.load, 500);
    }

    return this
};
