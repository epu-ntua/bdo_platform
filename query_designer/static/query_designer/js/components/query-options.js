/**
 * Created by dimitris on 17/5/2017.
 */
QueryOptions = function(qd) {
    var that = this;
    this.qd = qd;
    this.pages = {
        current: 0,
        total: 0
    };

    this.ui = {
        $elem: undefined,

        render: function() {
            this.$elem = $(
                '<div id="query-builder-options">' +
                    '<div class="checkbox">' +
                        '<label>Distinct' +
                            '<input type="checkbox" class="query-builder-options--distinct"><span class="checkbox-material"><span class="check"></span></span>' +
                        '</label>' +
                    '</div>' +
                    '<div class="form-group label-floating is-empty">' +
                        '<label class="control-label">Pattern</label>' +
                        '<input type="text" placeholder="e.g A + B" class="query-builder-options--pattern form-control">' +
                        '<span class="material-input"></span>' +
                    '</div>' +
                    '<div class="form-group label-floating is-empty">' +
                        '<label class="control-label">Limit</label>' +
                        '<input type="number" step="100" class="query-builder-options--limit form-control" value="100">' +
                        '<span class="material-input"></span>' +
                    '</div>' +
                    '<div class="form-group label-floating is-empty">' +
                        '<label class="control-label">Offset</label>' +
                        '<input type="number" step="100" class="query-builder-options--offset form-control" value="0">' +
                        '<span class="material-input"></span>' +
                    '</div>' +
                    '<button class="btn btn-sm pull-right btn-success">Run</button>' +
                '</div>'
            );

            $('body').append(this.$elem);

            this.$elem.dialog({
                title: 'Options',
                autoOpen: false,
                width: 600
            });

            // events
            this.$elem.find('button').on('click', function() {
                that.ui.close();
                that.qd.workbench.builder.reset();
                that.qd.queryExecutor.run();
            });
        },

        open: function() {
            this.$elem.dialog("open");
        },

        close: function() {
            this.$elem.dialog("close");
        }
    };

    this.hasNextPage = function() {
        var limit = this.getLimit(),
            offset = this.getOffset();

        return (offset / limit) + 1 < this.pages.total
    };

    this.toNextPage = function() {
        var limit = this.getLimit(),
            offset = this.getOffset();

        if (((offset / limit) + 1) >= this.pages.total) {
            return false;
        }

        setOffset(offset + limit);
        this.pages.current++;

        // re-run
        that.qd.workbench.builder.reset();
        that.qd.queryExecutor.run({
            scroll: false
        });
    };

    this.hasPrevPage = function() {
        var limit = this.getLimit(),
            offset = this.getOffset();

        return offset - limit > 0
    };

    this.toPrevPage = function() {
        var limit = this.getLimit(),
            offset = this.getOffset();

        if (offset - limit < 0) {
            return false
        }

        setOffset(limit - offset);
        this.pages.current--;

         // re-run
        that.qd.workbench.builder.reset();
        that.qd.queryExecutor.run({
            scroll: false
        });
    };

    this.setPages = function(pages) {
        this.pages = pages;
    };

    this.isDistinct = function() {
        return this.ui.$elem.find('.query-builder-options--distinct').is(":checked")
    };

    var setLimit = function(newLimit) {
        that.ui.$elem.find('.query-builder-options--limit').val(newLimit)
    };

    this.getLimit = function() {
        return Number(this.ui.$elem.find('.query-builder-options--limit').val()) || 100
    };

    var setOffset = function(newOffset) {
        that.ui.$elem.find('.query-builder-options--offset').val(newOffset)
    };

    this.getOffset = function() {
        return Number(this.ui.$elem.find('.query-builder-options--offset').val()) || 0
    };

    this.ui.render();

    return this;
};