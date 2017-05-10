BuilderWorkbenchFilters = function(qb) {
    var that = this;

    this.qb = qb;

    this.ui = {
        $elem: undefined,
        render: function() {
            this.$elem = $(
                '<div id="property-filters">' +
                    '<div class="filter-prototype">' +
                        '<select>' +
                            '<option value="and" selected="selected">All filters must be true</option>' +
                            '<option value="or">At least one filter needs to be true</option>' +
                            '<option value="nand">All filters must be false</option>' +
                            '<option value="nor">At least one filter needs to be false</option>' +
                            '<option value="custom">Specify a custom boolean expression</option>' +
                        '</select>' +
                        '<input type="text" id="filter-prototype-str" placeholder="e.g [1] && ([2] || [3])" />' +
                    '</div>' +
                    '<div id="all-filters">' +
                    '</div>' +
                    '<div class="select-filter-type">' +
                        '<span>Select filter type:</span>' +
                        '<select>' +
                            '<option value=""></option>' +
                            '<option value="str">String</option>' +
                            '<option value="num">Number</option>' +
                            '<option value="date">Date</option>' +
                            '<option value="value">URL</option>' +
                        '</select>' +
                        '<span id="filters-clear" class="btn btn-sm pull-right">Clear filters</span>' +
                    '</div>' +
                    '<div class="filter-type filter-type-str">' +
                        '<span>Value </span>' +
                        '<select>' +
                            '<option value="contains">contains</option>' +
                            '<option value="eq">is equal to</option>' +
                            '<option value="neq">not equal to</option>' +
                            '<option value="starts">starts with</option>' +
                            '<option value="ends">ends with</option>' +
                            '<option value="language">in language (if given): </option>' +
                            '<option value="regex">follows the regular expression:</option>' +
                        '</select>' +
                        '<input type="text" placeholder="value"/>' +
                        '<div class="right control-case-sensitive">' +
                            '<input type="checkbox" id="case-sensitive" default="false" />' +
                            '<label for="case-sensitive">Case sensitive</label>' +
                        '</div>' +
                    '</div>' +
                    '<div class="filter-type filter-type-num">' +
                        '<span>Value </span>' +
                        '<select>' +
                            '<option value="eq">=</option>' +
                            '<option value="neq">!=</option>' +
                            '<option value="lt">&lt;</option>' +
                            '<option value="lte">&lt;=</option>' +
                            '<option value="gt">&gt;</option>' +
                            '<option value="gte">&gt;=</option>' +
                        '</select>' +
                        '<input type="number" placeholder="value"/>' +
                    '</div>' +
                    '<div class="filter-type filter-type-date">' +
                        '<span>Value </span>' +
                        '<select>' +
                            '<option value="eq">=</option>' +
                            '<option value="neq">!=</option>' +
                            '<option value="lt">&lt;</option>' +
                            '<option value="lte">&lt;=</option>' +
                            '<option value="gt">&gt;</option>' +
                            '<option value="gte">&gt;=</option>' +
                        '</select>' +
                        '<input type="date" placeholder="value"/>' +
                    '</div>' +
                    '<div class="filter-type filter-type-value">' +
                        '<input type="url" placeholder="search for an entity">' +
                    '</div>' +
                    '<div class="clearfix">' +
                        '<span class="add-filter btn btn-sm btn-success pull-left">+Add filter</span>' +
                        '<span class="done btn btn-sm btn-primary pull-right">Save & close</span>' +
                    '</div>' +
                '</div>'
            );

            this.$elem.dialog({
                autoOpen: false,
                width: 600
            });
            this.$elem.show();

            // initially hide all categories
            this.$elem.find(".filter-type").hide();

            // hide custom prototype text
            this.$elem.find("#filter-prototype-str").hide();

            /*On filter prototype change*/
            this.$elem.find(".filter-prototype select").change(function() {
                var val = $(this).val();

                if (val == "custom" ) {
                    $("#filter-prototype-str").show();
                } else {
                    $("#filter-prototype-str").hide();
                }
            });

            /*On data type change*/
            this.$elem.find(".select-filter-type select").change(function() {
                var val = $(this).val();

                if (val == "str")
                    $("#property-filters .filter-type-str").show();
                else
                    $("#property-filters .filter-type-str").hide();

                if (val == "num")
                    $("#property-filters .filter-type-num").show();
                else
                    $("#property-filters .filter-type-num").hide();

                if (val == "date")
                    $("#property-filters .filter-type-date").show();
                else
                    $("#property-filters .filter-type-date").hide();

                if (val == "value")
                    $("#property-filters .filter-type-value").show();
                else
                    $("#property-filters .filter-type-value").hide();
            });

            /*String filter change*/
            this.$elem.find(".filter-type-str select").change(function() {
                if ($(this).val() == "language") {
                    $("#property-filters .filter-type-str .control-case-sensitive").hide();
                } else {
                    $("#property-filters .filter-type-str .control-case-sensitive").show();
                }
            });

            /* On add a filter click*/
            this.$elem.find(".add-filter").click(function() {
                //create the new filter object
                var nf = {};
                nf.type = $("#property-filters .select-filter-type select").val();
                nf.operator = $(".filter-type-" + nf.type + " select").val();
                nf.operator_label = $(".filter-type-" + nf.type + " select option:selected").text();
                nf.value = $(".filter-type-" + nf.type + " input").val();
                if (nf.type == "str") {
                    nf.case_sensitive = $("#case-sensitive").is(':checked');
                }

                //save the new filter and refresh
                that.qb.workbench.builder.property_selection.filters.push(nf);
                $(".filter-type-" + nf.type + " input").val('');
                that.show();
            });

            /* on done with filters click */
            this.$elem.find(".done").click(function() {
                var n = 0;
                var p = that.qb.workbench.builder.property_selection;
                var f_proto_val = $(".filter-prototype select").val();
                var proto = "";

                if ((f_proto_val == "and") || (f_proto_val == "or") || f_proto_val == "nand" || f_proto_val == "nor") { //automatically create the prototype
                    for (var f=0; f<p.filters.length; f++) {
                        if (p.filters[f] == undefined) continue;

                        n++;
                        if ((f_proto_val == "nand") || (f_proto_val == "nor")) {
                            proto += '!';
                        }
                        proto += '[' + f + ']';
                        if (f < p.filters.length - 1) {
                            if ((f_proto_val == "and") || (f_proto_val == "nand")) {
                                proto += ' && ';
                            } else {
                                proto += ' || ';
                            }
                        }
                    }
                } else { //get prototype from user
                    proto = $("#filter-prototype-str").val();

                    for (var f=0; f<p.filters.length; f++) {
                        if (p.filters[f] == undefined) continue;
                        n++;
                    }
                }

                p.filter_prototype = proto;
                $("#property-filters").dialog("close");

                //add icon to show which properties have filters
                if (n>0) {
                    $('#class_instance_' + that.qb.workbench.builder.property_selection_of_instance + ' .property-row:nth-of-type(' + (that.qb.workbench.builder.property_selection.n+2) + ') span:nth-of-type(5)').html('<span class="ui-icon ui-icon-check"></span>Edit');
                } else {
                    $('#class_instance_' + that.qb.workbench.builder.property_selection_of_instance + ' .property-row:nth-of-type(' + (that.qb.workbench.builder.property_selection.n+2) + ') span:nth-of-type(5)').html('Edit');
                }

                //reset the query
                that.qb.workbench.builder.reset();
            });

            /*On filter remove click*/
            this.$elem.on('click', '.filter-remove', function() {
                var f = $(this).data('about');
                that.qb.workbench.builder.property_selection.filters[f] = undefined;
                //TODO: better remove of filters
                if (f == that.qb.workbench.builder.property_selection.filters.length -1) { //last filter
                    that.qb.workbench.builder.property_selection.filters.pop();
                }
                that.show();
            });

            /*On filter clear click*/
            this.$elem.on('click', '#filters-clear', function() {
                that.qb.workbench.builder.property_selection.filters = [];
                that.show();
            });
        }
    };

    // render
    this.ui.render();

    this.show = function() {
        this.ui.$elem.dialog("open");
        this.ui.$elem.find("#all-filters").html('');

        if (this.qb.workbench.builder.property_selection) {
            var p = this.qb.workbench.builder.property_selection;
            var cnt = 0;

            //set dialog title
            $("#ui-id-1").text('<' + this.qb.workbench.builder.instances[this.qb.workbench.builder.property_selection_of_instance].label  + '>' + '.' + p.label);

            //show current filters
            $("#all-filters").html('');
            for (var i=0; i<p.filters.length; i++) {
                if (p.filters[i] == undefined) continue;

                cnt++;
                var label;
                if (p.filters[i].type == "value") {
                    label = '= ' + uri_to_label(p.filters[i].value);
                } else {
                    label = p.filters[i].operator_label + ' ' + p.filters[i].value;
                }

                $("#all-filters").append('<div class="filter-object">' + label + '<span class="filter-id">[' + i + ']</span><span class="filter-remove" data-about="' + i + '">x</span></div>');
            }

            if (cnt == 0) {
                $("#all-filters").html('No filters applied.');
                $('#filters-clear').css('display', 'none');
            } else {
                if (p.filter_prototype) { //restore filter type
                    if ((p.filter_prototype.indexOf("&&") < 0) && (p.filter_prototype.indexOf("||") < 0) && (p.filter_prototype.indexOf("![") < 0)) { //no operator -- default to AND
                        $(".filter-prototype select").val('and');
                        $("#filter-prototype-str").hide();
                    }
                    else if ((p.filter_prototype.indexOf("&&") >= 0) && (p.filter_prototype.indexOf("||") < 0) && (p.filter_prototype.indexOf("![") < 0)) { //AND join filters
                        $(".filter-prototype select").val('and');
                        $("#filter-prototype-str").hide();
                    }
                    else if ((p.filter_prototype.indexOf("&&") < 0) && (p.filter_prototype.indexOf("||") >= 0) && (p.filter_prototype.indexOf("![") < 0)) { //OR join filters
                        $(".filter-prototype select").val('or');
                        $("#filter-prototype-str").hide();
                    }
                    else if ((p.filter_prototype.indexOf("||") < 0) && (p.filter_prototype.indexOf(" [") < 0)) { //NAND join filters
                        $(".filter-prototype select").val('nand');
                        $("#filter-prototype-str").hide();
                    }
                    else if ((p.filter_prototype.indexOf("&&") < 0) && (p.filter_prototype.indexOf("||") >= 0) && (p.filter_prototype.indexOf(" [") < 0)) { //NOR join filters
                        $(".filter-prototype select").val('nor');
                        $("#filter-prototype-str").hide();
                    }
                    else { //CUSTOM join filter boolean expression
                        $(".filter-prototype select").val('custom');
                        $("#filter-prototype-str").val(p.filter_prototype);
                        $("#filter-prototype-str").show();
                    }
                }

                //show the clear filters button
                $('#filters-clear').css('display', 'inline-block');
            }

            /*Find specific value autocomplete*/
            if (this.qb.workbench.builder.property_selection.uri == "URI") {
                $(".filter-type-value input").autocomplete({
                    source: "/query-designer/api/suggest/" + this.qb.workbench.builder.instances[this.qb.workbench.builder.property_selection_of_instance].dt_name + "/?class_uri=" +
                                                     encodeURIComponent(this.qb.workbench.builder.instances[this.qb.workbench.builder.property_selection_of_instance].uri),
                });
            } else {
             $(".filter-type-value input").autocomplete({
                    source: "/query-designer/api/suggest/" + this.qb.workbench.builder.instances[this.qb.workbench.builder.property_selection_of_instance].dt_name + "/?class_uri=" +
                                                     encodeURIComponent(this.qb.workbench.builder.instances[this.qb.workbench.builder.property_selection_of_instance].uri) +
                                                     "&property_uri=" + encodeURIComponent(this.qb.workbench.builder.property_selection.uri)
                });
            }
        }
    };

    return this;
};

