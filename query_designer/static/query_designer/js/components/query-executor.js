/**
 * Created by dimitris on 12/5/2017.
 */
QueryExecutor = function(qd) {
    var that = this;

    this.qd = qd;

    this.ui = {
        $elem: undefined,

        render: function() {
            this.$elem = $('' +
                '<div class="row">' +
                    '<div class="col-xs-12">' +
                        '<h3>Results</h3>' +
                        '<div class="card card-nav-tabs">' +
                            '<div class="card-header" data-background-color="orange">' +
                                '<div class="nav-tabs-navigation">' +
                                    '<div class="nav-tabs-wrapper">' +
                                        '<span class="nav-tabs-title">Tasks:</span>' +
                                        '<ul class="nav nav-tabs" data-tabs="tabs">' +
                                            '<li class="active">' +
                                                '<a href="#query-results--visualization" data-toggle="tab" aria-expanded="true">' +
                                                    '<i class="material-icons">bug_report</i>' +
                                                    'Overview' +
                                                '<div class="ripple-container"></div></a>' +
                                            '</li>' +
                                            '<li>' +
                                                '<a href="#query-results--data" data-toggle="tab" aria-expanded="false">' +
                                                    '<i class="material-icons">code</i>' +
                                                    'Data' +
                                                '<div class="ripple-container"></div></a>' +
                                            '</li>' +
                                        '</ul>' +
                                    '</div>' +
                                '</div>' +
                            '</div>' +
                            '<div class="card-content">' +
                                '<div class="tab-content">' +
                                    '<div class="tab-pane active" id="query-results--visualization">' +
                                    '</div>' +
                                    '<div class="tab-pane" id="query-results--data">' +
                                        '<table class="table table-hover">' +
                                        '</table>' +
                                    '</div>' +
                                '</div>' +
                            '</div>' +
                        '</div>' +
                    '</div>' +
                '</div>'
            );

            // add to query designer
			that.qd.$container.append(this.$elem);
        },

        clear: function() {
            this.$elem
                .find('#query-results--visualization')
                .empty()
                .append($('<p />').text('No results'));

            this.$elem
                .find('#query-results--data')
                .empty()
                .append($('<p />').text('No data loaded'));
        },

        setLoading: function() {
            this.$elem
                .find('#query-results--visualization')
                .empty()
                .append($('<p />').text('Loading...'));

            this.$elem
                .find('#query-results--data')
                .empty()
                .append($('<p />').text('Loading...'));
        },

        renderResults: function(data) {
            var $dataTable = $('<table />').addClass('table');
            $dataTable.append($('<thead />').addClass('text-warning'));
            $dataTable.append($('<tbody />'));

            // add headers
            var $headRow = $('<tr />');
            $headRow.append($('<th />').text('#'));
            $.each(data.headers.columns, function(idx, column) {
                $headRow.append($('<th />').text(column.title));
            });
            $dataTable.find('> thead').append($headRow);

            // add results
            var $tbody = $dataTable.find('> tbody');
            $.each(data.results, function(idx, result) {
                var $tr = $('<tr />');
                $tr.append($('<td />').text(idx + 1));
                $.each(result, function(idx, resultValue) {
                    $tr.append($('<td />').text(resultValue));
                });
                $tbody.append($tr);
            });

            // add data table
            this.$elem
                .find('#query-results--data')
                .empty()
                .append($dataTable);
        }
    };

    this.run = function() {
        var config = that.qd.config.endpoint,
            requestParameters = jQuery.extend(true, {}, config.defaultParameters);

        // add query property
        requestParameters[config.queryParameter] = that.qd.workbench.query;
        that.ui.setLoading();

        $.ajax({
            'url': config.url,
            'type': config.type,
            'data': requestParameters,
            success: function(data) {
                console.log(data);
                that.ui.renderResults(data)
            }
        })
    };

    this.ui.render();
    this.ui.clear();

    /* F9 to run query */
	$("body").on('keyup', function(e) {
	    if (e.keyCode == 120) { // F9 key pressed
            that.run();
        }
    });

    return this;
};