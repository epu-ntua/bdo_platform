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
                '<div class="row" id="query-results--container">' +
                    '<div class="col-xs-12">' +
                        '<h3>Results</h3>' +
                        '<div class="card card-nav-tabs">' +
                            '<div class="card-header" data-background-color="blue">' +
                                '<div class="nav-tabs-navigation">' +
                                    '<div class="nav-tabs-wrapper">' +
                                        '<ul class="nav nav-tabs" data-tabs="tabs">' +
                                            '<li class="active">' +
                                                '<a href="#query-results--visualization" data-toggle="tab" aria-expanded="true">' +
                                                    '<i class="material-icons">perm_media</i>' +
                                                    'Overview' +
                                                '<div class="ripple-container"></div></a>' +
                                            '</li>' +
                                            '<li>' +
                                                '<a href="#query-results--data" data-toggle="tab" aria-expanded="false">' +
                                                    '<i class="material-icons">code</i>' +
                                                    'Data' +
                                                '<div class="ripple-container"></div></a>' +
                                            '</li>' +
                                            '<li class="pull-right page-next disabled"><a href="#"><i class="material-icons">chevron_right</i><div class="ripple-container"></div></a></li>' +
                                            '<li class="pull-right page-info"><span style="margin-top: 10px;display: block;"></span></li>' +
                                            '<li class="pull-right page-prev disabled"><a href="#"><i class="material-icons">chevron_left</i><div class="ripple-container"></div></a></li>' +
                                        '</ul>' +
                                    '</div>' +
                                '</div>' +
                            '</div>' +
                            '<div class="card-content">' +
                                '<div class="tab-content" style="min-height: 490px;">' +
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

            // add events
            this.$elem.find('li.page-prev > a').on('click', function(e) {
                e.preventDefault();
                e.stopPropagation();

                that.qd.options.toPrevPage();
            });

            this.$elem.find('li.page-next > a').on('click', function(e) {
                e.preventDefault();
                e.stopPropagation();

                that.qd.options.toNextPage();
            });

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

        updatePageInfo: function() {
            // update buttons
            if (that.qd.options.hasPrevPage()) {
                this.$elem.find('li.page-prev').removeClass('disabled')
            } else {
                this.$elem.find('li.page-prev').addClass('disabled')
            }

            if (that.qd.options.hasNextPage()) {
                this.$elem.find('li.page-next').removeClass('disabled')
            } else {
                this.$elem.find('li.page-next').addClass('disabled')
            }

            // show message
            this.$elem.find('li.page-info > span').text('Page ' + that.qd.options.pages.current +
                                                        ' of ' + that.qd.options.pages.total);
        },

        renderResults: function(data, scroll) {
            if (scroll === undefined) {
                scroll = true;
            }

            var $dataTable = $('<table />').addClass('table');
            $dataTable.append($('<thead />').addClass('text-info'));
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

                // TODO add message for trimmed results
                if (idx >= 200) {
                    return false;
                }

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

            // create & add chart
            new ChartBuilder(that.qd, '#query-results--visualization', data.headers.columns);

            // scroll to results
            if (scroll) {
                that.qd.config.scrollParent.animate({
                    scrollTop: $('#query-results--container').position().top
                }, 500, 'swing');
            }
        }
    };

    this.run = function(runConfig) {
        runConfig = $.extend({}, {
            scroll: true,
            callback: undefined,
            extraFilters: [],
            variable: undefined,
            dimensionValues: undefined,
            onlyHeaders: false,
            noPagination: false
        }, runConfig);

        var config = that.qd.config.endpoint,
            requestParameters = jQuery.extend(true, {}, config.defaultParameters);

        // add query property
        var query = that.qd.workbench.query,
            queryDocument = undefined;
        if (runConfig.extraFilters.length > 0 || runConfig.noPagination) {
            queryDocument = new DocumentBuilder(that.qd).getDocument();
        }

        // add extra filters
        if (runConfig.extraFilters.length > 0) {
            $.each(runConfig.extraFilters, function(idx, f) {
                queryDocument.filters.push(f);
            })
        }

        if (runConfig.noPagination) {
            queryDocument.limit = undefined;
            queryDocument.offset = undefined;
        }

        if (queryDocument !== undefined) {
            query = that.qd.config.language.parser(queryDocument).getQuery();
        }

        // construct params
        requestParameters[config.queryParameter] = query;
        if (runConfig.onlyHeaders === true) {
            requestParameters['only_headers'] = 'true';
        }
        if (runConfig.dimensionValues !== undefined) {
            requestParameters['dimension_values'] = runConfig.dimensionValues;
        }
        if (runConfig.variable !== undefined) {
            requestParameters['variable'] = runConfig.variable;
        }

        if (runConfig.callback === undefined) {
            that.ui.setLoading();
        }

        $.ajax({
            'url': config.url,
            'type': config.type,
            'data': requestParameters,
            success: function(data) {

                // if custom callback is set, run that instead
                if (runConfig.callback !== undefined) {
                    return runConfig.callback(data);
                }

                that.ui.renderResults(data, runConfig.scroll);

                // update query options with page info
                that.qd.options.setPages(data.headers.pages);

                // update prev/next arrows
                that.ui.updatePageInfo();
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