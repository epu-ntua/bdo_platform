/**
 * Created by dimitris on 17/5/2017.
 */
QueryOptions = function(qd) {
    var that = this;
    this.pages = {
        current: 0,
        total: 0
    };

    this.ui = {
        $elem: undefined,

        render: function() {
            this.$elem = $(
                '<div id="query-builder-options">' +
                    '<label>Variables:</label><div id="query-builder-options--variables"></div><br />' +
                    '<div class="checkbox">' +
                        '<label>Distinct' +
                            '<input type="checkbox" id="query-builder-options--distinct"><span class="checkbox-material"><span class="check"></span></span>' +
                        '</label>' +
                    '</div>' +
                    '<div class="form-group label-floating is-empty">' +
                        '<label class="control-label">Pattern</label>' +
                        '<input id="query-builder-options--pattern" type="text" placeholder="e.g A + B" class="form-control">' +
                        '<span class="material-input"></span>' +
                    '</div>' +
                    '<div class="form-group label-floating is-empty">' +
                        '<label class="control-label">Limit</label>' +
                        '<input id="query-builder-options--limit" type="number" step="100" class="form-control" value="100">' +
                        '<span class="material-input"></span>' +
                    '</div>' +
                    '<div class="form-group label-floating is-empty">' +
                        '<label class="control-label">Offset</label>' +
                        '<input id="query-builder-options--offset" type="number" step="100" class="form-control" value="0">' +
                        '<span class="material-input"></span>' +
                    '</div>' +
                    '<button id="query-builder-options--update" class="btn btn-sm pull-right btn-success">OK</button>' +
                '</div>'
            );

            $('body').append(this.$elem);

            this.$elem.dialog({
                title: 'Options',
                autoOpen: false,
                width: 600
            });
        },

        open: function() {
            this.$elem.dialog("open");
        },

        close: function() {
            this.$elem.dialog("close");
        }
    };

    this.toNextPage = function() {

    };

    this.toPrevPage = function() {

    };

    this.setPages = function(pages) {
        this.pages = pages;
    };

    this.getLimit = function() {
        return Number(this.ui.$elem.find('#query-builder-options--limit').val()) || 100
    };

    this.getOffset = function() {
        return Number(this.ui.$elem.find('#query-builder-options--offset').val()) || 0
    };

    this.ui.render();

    return this;
};