/**
 * Created by dimitris on 23/6/2017.
 */
QueryStorage = function(qd, pk) {
    var that = this;

    this.qd = qd;
    this.pk = pk;
    this.title = undefined;

    this.ui = {
        $elem: undefined,

        render: function() {
            this.$elem = $(
                '<div id="query-rename-dlg">' +
                    '<div class="checkbox">' +
                        '<label class="full-width">Provide a discription for this query <br />' +
                            '<input type="text" id="query-storage--title" class="form-control full-width" style="margin-top: 15px; width: calc(100% - 100px);">' +
                            '<span class="material-input"></span>' +
                        '</label>' +
                    '</div>' +
                    '<button class="btn btn-sm pull-right bg-color--orange save-query--submit"><i class="fa fa-save"></i> Save</button>' +
                '</div>'
            );

            $('body').append(this.$elem);

            this.$elem.dialog({
                title: 'Save query',
                autoOpen: false,
                width: 600
            });
        },

        open: function(callback) {
            var fn = function() {
                that.ui.close();
                callback(that.ui.$elem.find('#query-storage--title').val());
            };

            // events
            this.$elem.on('click', '.save-query--submit', function() {fn();});
            this.$elem.on('keypress', '#query-storage--title', function(e) {
                if (e.which === 13) {
                    e.preventDefault();
                    e.stopPropagation();
                    fn();
                }
            });

            this.$elem.dialog("open");
            this.$elem.find('#query-storage--title').focus();
        },

        close: function() {
            this.$elem.dialog("close");
        },

        updateTitle: function() {
            var $title = $('.designer-menu .query-title');

            if (that.pk !== undefined) {
                $title.text('#' + that.pk + ': ' + that.title)
            } else {
                $title.text('')
            }
        }
    };

    this.load = function() {
        $.ajax({
            url: '/queries/load/' + pk + '/',
            type: 'GET',
            success: function(qObj) {
                that.pk = qObj.pk;
                that.title = qObj.title;
                qd.workbench.builder.fromJson(qObj.design);

                that.ui.updateTitle();
            }
        })
    };

    this.save = function(title) {
        var postEndpoint = "/queries/save/";
        if (pk !== undefined) {
            postEndpoint += pk + '/'
        }

        var _save = function(title) {
            var data = {
                document: JSON.stringify(new DocumentBuilder(that.qd).getDocument()),
                design: JSON.stringify(qd.workbench.builder.toJson())
            };

            if (title !== undefined) {
                data.title = title;
            }

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

                    // store PK & update URL
                    that.pk = qObj.pk;
                    that.title = qObj.title;
                    window.history.replaceState({} , title, '/queries/' + qObj.pk + '/');

                    // query title
                    that.ui.updateTitle();
                },
                error: function (jqXHR) {
                    $("#alert_modal .modal-title").html('Error');
                    $("#alert_modal .modal-body").html(jqXHR.responseText);
                    $("#alert_modal .modal-footer .btn-default").html('OK');
                    $("#alert_modal").show();
                }
            });
        };

        // ask for title for new queries
        if (this.pk === undefined) {
            this.ui.open(_save);
        } else {
            _save();
        }
    };

    this.load_to_analysis = function() {
        var document = JSON.stringify(new DocumentBuilder(that.qd).getDocument());
        var data = {
            document: document,
            title: 'New query'
        };
        $.ajax({
            url: '/queries/load_to_analysis/',
            data: data,
            type: 'GET',
            success: function(qObj) {
                // TODO load new query to analysis
                opener.addNewQuery(qObj.title, qObj.raw_query, document);
                close();
            },
            error: function () {
                alert('New query could not be loaded to the analysis');
                // TODO maybe use alert modal
            }
        })
    };

    this.ui.render();

    if (this.pk !== undefined) {
        setTimeout(this.load, 500);
    }

    /* Ctrl+S to save query */
    document.addEventListener("keydown", function(e) {
        if (e.keyCode == 83 && e.ctrlKey) { //
            that.qd.storage.save();

            e.preventDefault();
            e.stopPropagation();
        }
    }, false);

    return this
};
