/**
 * Created by dimitris on 15/9/2017.
 */
var PropertyOptions = function(qd) {
    var that = this;

    this.i = undefined;
    this.p = undefined;
    this.instance = undefined;
    this.property = undefined;
    this.prev_name = undefined;

    this.ui = {
        $elem: undefined,
        render: function() {
            this.$elem = $(
                '<div class="form">' +
                    '<div style="display: none">' +
                        '<label>URI</label>' +
                        '<label class="property-uri"></label>' +
                    '</div>' +
                    '<div class="form-group label-floating">' +
                        '<label class="control-label">Variable name</label>' +
                        '<input class="property-name form-control" type="text"/>' +
                        '<span class="material-input"></span>' +
                    '</div>' +
                    '<div class="checkbox">' +
                        '<label>Group by' +
                            '<input class="property-group-by" type="checkbox"/>' +
                            '<span class="checkbox-material"><span class="check"></span></span>' +
                        '</label>' +
                    '</div>' +
                    '<div class="form-group">' +
                        '<div><label>Aggregate</label></div>' +
                        '<select class="property-aggregate form-control">' +
                            '<option value=""></option>' +
                            '<option value="sum">Sum</option>' +
                            '<option value="count">Count</option>' +
                            '<option value="avg">Average</option>' +
                            '<option value="min">Minimum</option>' +
                            '<option value="max">Maximum</option>' +
                        '</select>' +
                    '</div>' +
                    '<button class="btn btn-sm pull-right btn-success options-save">OK</button>' +
                '</div>'
            );

            // add to page
            $('body').append(this.$elem);

            // element is a dialog
            this.$elem.dialog({
                autoOpen: false,
                width: 600
            });

            this.$elem.find('.options-save').on('click', function() {
                that.ui.$elem.dialog("close");

                that.save();
                qd.workbench.builder.reset();
            });
        },

        setTitle: function(newTitle) {
            this.$elem.parent().find('.ui-dialog-title').text(newTitle);
        }
    };

    this.show = function(i, p) {
        this.i = i;
        this.p = p;
        this.instance = qd.workbench.builder.instances[i];
        this.property = this.instance.selected_properties[p];

        // set dialog title
        this.ui.setTitle('Property options (' + this.property.name + ')');

        // uri
        if (this.property.uri == 'URI') {
            this.ui.$elem.find('.property-uri').html('&lt;' + this.instance.uri + '&gt;');
        } else {
            this.ui.$elem.find('.property-uri').html('&lt;' + this.property.uri + '&gt;');
        }

        // name
        this.prev_name = this.property.name;
        this.ui.$elem.find('.property-name').val(this.property.name);

        // group by
        this.ui.$elem.find('.property-group-by').attr('checked', this.property.groupBy === true);

        // aggregate
        if (this.property.aggregate !== undefined) {
            this.ui.$elem.find('.property-aggregate').val(this.property.aggregate);
        } else {
            this.ui.$elem.find('.property-aggregate').val("");
        }

        // show dialog
        this.ui.$elem.dialog("open");
    };

    this.getCurrentProperty = function() {
        return this.propertyNameFromString(this.instance.id, this.property.uri, this.property.name);
    };

    this.propertyNameFromString = function(i, p_uri, p_name) {
        if (p_uri == "URI") {
            return "URI";
        }

        var result = p_name.replace(/_/g, ' ').replace(qd.workbench.builder.instanceNames[i], '').trim();
        return result.charAt(0).toUpperCase() + result.slice(1);
    };

    this.save = function() {
        //save changes
        //change name in builder & workbench
        if (this.ui.$elem.find('.property-name').val() != this.prev_name) {
            this.property.name = this.ui.$elem.find('.property-name').val();
			if (this.property.name == "") {
				this.property.name_from_user = false;
				builder.reset();
			} else {
				this.property.name_from_user = true;
			}
            $("#class_instance_" + this.i + " .property-row:nth-of-type(" + (this.p+2) + ") span:nth-of-type(2)").html(this.getCurrentProperty());
        }

        this.property.groupBy = this.ui.$elem.find('.property-group-by').is(":checked");
        this.property.aggregate = this.ui.$elem.find('.property-aggregate').val();
        if (this.property.aggregate === "") {
            this.property.aggregate = undefined;
        }
    };

    this.ui.render();

    return this
};
