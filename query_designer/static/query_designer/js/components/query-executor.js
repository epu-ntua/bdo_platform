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
                                        '</ul>' +
                                    '</div>' +
                                '</div>' +
                            '</div>' +
                            '<div class="card-content">' +
                                '<div class="tab-content" style="min-height: 490px;">' +
                                    '<div class="tab-pane active" id="query-results--visualization">' +
                                    '</div>' +
                                    '<div class="tab-pane" id="query-results--data">' +
                                        '<div class="row">' +
                                            '<ul class="paginator pull-right">' +
                                                '<li class="page-prev disabled"><a href="#"><i class="material-icons">chevron_left</i><div class="ripple-container"></div></a></li>' +
                                                '<li class="page-info"><span style="margin-top: 10px;display: block;"></span></li>' +
                                                '<li class="page-next disabled"><a href="#"><i class="material-icons">chevron_right</i><div class="ripple-container"></div></a></li>' +
                                            '</ul>' +
                                        '</div>'+
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
                .find('#query-results--data table')
                .empty()
                .append($('<tr />').append($('<td />').text('No data loaded')));
        },

        setLoading: function(setChartLoading) {
            if (setChartLoading === undefined) {
                setChartLoading = true;
            }

            if (setChartLoading) {
                this.$elem
                    .find('#query-results--visualization')
                    .empty()
                    .append($('<p />').text('Loading...'));
            }

            this.$elem
                .find('#query-results--data table')
                .empty()
                .append($('<tr />').append($('<td />').addClass('loading').text('Loading...')));
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
            this.$elem.find('li.page-info > span').text('Page ' + that.qd.options.pages.current.toLocaleString() +
                                                        ' of ' + that.qd.options.pages.total.toLocaleString());
        },

        renderResults: function(data, updateChart, scroll) {
            if (scroll === undefined) {
                scroll = true;
            }
            if (updateChart === undefined) {
                updateChart = true;
            }

            var $dataTable = this.$elem
                .find('#query-results--data table').empty();
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

                var trimLimit = 500;
                if (idx >= trimLimit) {
                    $tbody.append($('<tr />').append($('<td />')).append($('<td />').text('No more than ' + trimLimit + ' results can be shown')));
                    return false;
                }

                var $tr = $('<tr />');
                $tr.append($('<td />').text(idx + 1));
                $.each(result, function(idx, resultValue) {
                    $tr.append($('<td />').text(resultValue));
                });
                $tbody.append($tr);
            });

            // create & add chart
            if (updateChart) {
                new ChartBuilder(that.qd, '#query-results--visualization', data.headers.columns);
            }

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
            extraFilters: undefined,
            variable: undefined,
            dimensionValues: undefined,
            onlyHeaders: false,
            noPagination: false,
            updateChart: true
        }, runConfig);

        var config = that.qd.config.endpoint,
            requestParameters = jQuery.extend(true, {}, config.defaultParameters),
            runEndpointSuffix = '';

        // add query property
        var query = that.qd.workbench.query,
            queryDocument = undefined;
        if (runConfig.extraFilters !== undefined || runConfig.noPagination) {
            queryDocument = new DocumentBuilder(that.qd).getDocument();
        }

        // add extra filters
        if (runConfig.extraFilters !== undefined) {
            if (queryDocument.filters === undefined) {
                queryDocument.filters = runConfig.extraFilters;
            }
            else if (runConfig.extraFilters !== undefined) {
                queryDocument.filters = {
                    "a": JSON.parse(JSON.stringify(queryDocument.filters)),
                    "op": "AND",
                    "b": runConfig.extraFilters
                }
            }
        } else if (!runConfig.onlyHeaders) {
            runEndpointSuffix = (that.qd.storage.pk !== undefined?that.qd.storage.pk + '/':'');
        }

        if (runConfig.noPagination) {
            queryDocument.limit = undefined;
            queryDocument.offset = undefined;
        }

        if (runConfig.pagination) {
            queryDocument.limit = runConfig.pagination.limit;
            queryDocument.offset = runConfig.pagination.offset;
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
            that.ui.setLoading(runConfig.updateChart);
        }

        $.ajax({
            'url': config.url + runEndpointSuffix,
            'type': config.type,
            'data': requestParameters,
            success: function(data) {

                // if custom callback is set, run that instead
                if (runConfig.callback !== undefined) {
                    return runConfig.callback(data);
                }

                that.ui.renderResults(data, runConfig.updateChart, runConfig.scroll);

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