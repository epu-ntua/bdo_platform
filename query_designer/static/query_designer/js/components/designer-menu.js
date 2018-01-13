/**
 * Created by dimitris on 16/5/2017.
 */
DesignerMenu = function(qd) {
    var that = this;

    this.qd = qd;

    this.ui = {
        $elem: undefined,

        render: function() {
            var elemString = '<div class="designer-menu">' +
                            '<div class="btn-group">' +
                            '<button class="btn btn-sm bg-color--lightgray execute-query" title="Run (F9)"><i class="material-icons text-green">play_arrow</i> Run(F9)</button>' +
                            '<button class="btn btn-sm bg-color--lightgray save-query" title="Save (Ctrl+S)"><i class="material-icons text-orange">save</i> Save</button>';
            if(window.opener && !window.opener.closed) {
                elemString += '<button class="btn btn-sm bg-color--lightgray query-to-analysis" title="Load query to analysis"><i class="material-icons text-blue">input</i> Load to analysis</button>';
            }
            elemString += '</div>' +
                        '<div class="pull-right">' +
                        '<span class="query-title"></span>' +
                        '<div class="btn-group">' +
                        '<button class="btn btn-sm bg-color--lightgray view-code hidden"><i class="material-icons text-gray">code</i> View Code</button>' +
                        '<button class="btn btn-sm bg-color--lightgray advanced-view"><i class="material-icons text-gray">code</i> Advanced view</button>' +
                        '<button class="btn btn-sm bg-color--lightgray show-query-options"><i class="material-icons text-gray">settings</i> Options</button>' +
                        '</div>' +
                        '</div>' +
                        '</div>';

                this.$elem = $(elemString);

            // add events
            this.$elem.find('.execute-query').on('click', function() {
                that.qd.queryExecutor.run();
            });

            this.$elem.find('.save-query').on('click', function() {
                that.qd.storage.save();
            });

            this.$elem.find('.query-to-analysis').on('click', function() {
                that.qd.storage.load_to_analysis();
            });

            this.$elem.find('.show-query-options').on('click', function() {
                that.qd.options.ui.open();
            });

            this.$elem.find('.advanced-view').on('click', function() {
                that.qd.$container.toggleClass('expanded');
            });

            // add menu to designer
            that.qd.$container.prepend(this.$elem);
        },

        setRunning: function() {
            this.$elem.find('.execute-query')
                .html('<i class="material-icons text-green">play_arrow</i> Running...')
                .attr('disabled', 'disabled');
        },

        setRunComplete: function() {
            this.$elem.find('.execute-query')
                .html('<i class="material-icons text-green">play_arrow</i> Run(F9)')
                .removeAttr('disabled');
        }
    };

    this.ui.render();

    return this;
};