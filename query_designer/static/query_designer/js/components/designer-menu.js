/**
 * Created by dimitris on 16/5/2017.
 */
DesignerMenu = function(qd) {
    var that = this;

    this.qd = qd;

    this.ui = {
        $elem: undefined,

        render: function() {
            this.$elem = $(
                '<div class="designer-menu">' +
                    '<div class="btn-group">' +
                        '<button class="btn btn-sm bg-color--lightgray execute-query" title="Run (F9)"><i class="material-icons text-green">play_arrow</i> Run(F9)</button>' +
                        '<button class="btn btn-sm bg-color--lightgray save-query" title="Save (Ctrl+S)"><i class="material-icons text-orange">save</i> Save</button>' +
                    '</div>' +
                    '<div class="pull-right">' +
                        '<span class="query-title"></span>' +
                        '<div class="btn-group">' +
                            '<button class="btn btn-sm bg-color--lightgray view-code"><i class="material-icons text-gray">code</i> View Code</button>' +
                            '<button class="btn btn-sm bg-color--lightgray show-query-options"><i class="material-icons text-gray">settings</i> Options</button>' +
                        '</div>' +
                    '</div>' +
                '</div>'
            );

            // add events
            this.$elem.find('.execute-query').on('click', function() {
                that.qd.queryExecutor.run();
            });

            this.$elem.find('.save-query').on('click', function() {
                that.qd.storage.save();
            });

            document.addEventListener("keydown", function(e) {
                if (e.keyCode == 83 && e.ctrlKey) { //Ctrl+S key pressed
                    that.qd.storage.save();

                    e.preventDefault();
                    e.stopPropagation();
                }
            }, false);

            this.$elem.find('.show-query-options').on('click', function() {
                that.qd.options.ui.open();
            });

            // add menu to designer
            that.qd.$container.prepend(this.$elem);
        }
    };

    this.ui.render();

    return this;
};