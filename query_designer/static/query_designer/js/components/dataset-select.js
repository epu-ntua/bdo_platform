/**
 * Created by dimitris on 4/5/2017.
 */
DatasetSelect = function(qd) {
    var that = this;

    this.config = qd.config.datasetSelect;
    this.qd = qd;
    this.datasets = [];

    this.load = function() {

        if (that.config.source instanceof Array) {
            that.datasets = that.config.source;
            that.ui.updateDatasets();
        }
        else if (that.config.source.type === 'GET') {
            //make request for dataset structure
            $.ajax({
                url: that.config.source.from,
                type: "GET",
                success: function(datasets) {
                    that.datasets = datasets;
                    that.ui.updateDatasets();
                }
            });
        } else {
            throw Error('Invalid dataset source');
        }
    };

    this.getDatasetId = function() {
        return this.ui.$elem.val();
    };

    this.getDatasetFromId = function(_id) {
        var resultDataset = null;
        $.each(this.datasets, function(idx, dataset) {
            if (dataset._id === _id) {
                resultDataset = dataset;
                return false;
            }
        });

        return resultDataset;
    };

    this.ui = {
        $elem: undefined,

        updateDatasets: function() {
            this.$elem.empty();

            this.$elem.append($('<option />')
                .attr('val', '')
                .text('Choose a ' + that.config.title.toLowerCase())
            );

            $.each(that.datasets, function(idx, dataset) {
                var $option = $('<option />')
                    .attr('value', dataset._id)
                    .text(dataset.title);

                if (dataset.default === true) {
                    $option
                        .attr('selected', 'selected');
                }

                that.ui.$elem.append($option);
            });

            this.$elem.trigger('change');
        },

        render: function() {
            this.$elem = $('<select />')
                .addClass('form-control');
        }
    };

    // render
    this.ui.render();

    // load
    this.load();
};