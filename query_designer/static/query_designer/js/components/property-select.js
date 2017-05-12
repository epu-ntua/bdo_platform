/**
 * Created by dimitris on 4/5/2017.
 */
function PropertySelect(qd, instance) {
    this.qd = qd;
    this.c = instance;
    this.properties = [];
    this.page = 0;
    this.started_loading = false;
    this.finished_loading = false;
    this.PROPERTY_PAGE_LIMIT = 200;
    this.SELECT_SIZE = 25;
    this.offset = 0;

    var that = this;

    this.load_property_page = function(p) {
        var that = this;
        var c = this.c;

        var propertyUrl = that.qd.workbench.config.propertySource.from
                    .replace('{{ datasetId }}', that.c.dt_name)
                    .replace('{{ variableId }}', that.c.uri);

        // make an ajax request to get properties
        $.ajax({
            url: propertyUrl,
            type: "GET",
            success: function(data) {
                // check if the instance was deleted in the mean time
                if (!c || that.to_stop) {
                    return;
                }

                if (p > 0) {
                    that.started_loading = true;
                }

                // pack some properties
                data = that.qd.config.properties.pack(data);

                // add the properties
                for (var i=0; i<data.length; i++) {
                    // properties found from the vocabulary are not certain to exist in the data source
                    var o = {'uri': data[i]._id, 'label': data[i].title, 'uncertain': false, info: data};

                    o.frequence = undefined;

                    that.properties.push(o);

                    // add to instance by default
                    that.qd.workbench.builder.add_property(that.c.id, o.uri, o.label, o.info);
                }

                that.repeating_pages = 0;
                $("#class_instance_" + that.c.id + " .property-control .properties-found").html(Number(that.properties.length).toLocaleString() + ' properties found');

                that.show();
                that.finished_loading = true;
            },
            error: function (jqXHR, textStatus, errorThrown) {
                console.log(textStatus + ': ' + errorThrown);
                if (qd.workbench.builder.instances[that.c.id].property_select.properties.length == 0) {
                    var $ci = $("#class_instance_" + that.c.id);
                    $ci.find('.dropdown-toggle-properties > span')
                        .removeClass("loading")
                        .addClass("error")
                        .html('X');

                    $ci.find(' .property-control .properties-found').html('Could not load properties');
                }
            }
        });
    };

    this.load = function() { // load the current page of properties
        var that = this;

        if (this.to_stop) {
            return;
        }

        this.repeating_pages = 0;
        this.load_property_page(0);
    };

    this.stop = function() {
        this.to_stop = true;
    };

    this.show = function() {
        var filter = $("#class_instance_" + this.c.id + " .property-control input").val();
        var added = 0;
        var total = 0;
        var limit = this.SELECT_SIZE;
        var offset = (this.page)*limit;
        var $propertyControl = $("#class_instance_" + this.c.id + " .property-control");
        $propertyControl.find(".property-dropdown .properties-list").html('');
        $propertyControl.find(".dropdown-toggle-properties > span").removeClass("loading");
        $propertyControl.find(".dropdown-toggle-properties > span").html('');
        $propertyControl.find(".dropdown-toggle-properties > span").addClass("caret");

        if (this.page > 1) { // previous page
            $propertyControl.find(".property-dropdown .up").html('&uarr; results ' + (offset + 1) + ' - ' + (offset + limit));
            $propertyControl.find(".property-dropdown .up").show();
        } else {
            $propertyControl.find(".property-dropdown .up").hide();
        }

        for (var i=0; i<this.properties.length; i++) { //foreach property loaded until now
            var label = this.properties[i].label;

            if (!filter || (label.toLowerCase().indexOf(filter.toLowerCase()) >= 0)) {
                total++;

                if ((total >= offset) && (total < offset + limit)) {
                    var data_str = 'data-uri="' + this.properties[i].uri + '"';

                    //create the property html object
                    var class_str = 'class="property';
                    if (this.properties[i].uncertain === true) {
                        class_str += ' uncertain';
                    }
                    class_str += '"';

                    var property_div = '<div ' + class_str + ' ' + data_str + '>' + label;
                    if (this.properties[i].frequence !== undefined) {
                        property_div += ' (' + this.properties[i].frequence + ')';
                    }
                    property_div += '</div>';

                    //append the property to the select
                    $propertyControl.find(".property-dropdown .properties-list").append(property_div);
                    added++;
                }

                if (added == limit) {
                    break;
                }
            }
        }

        if (added == limit) { // there are more than those that are shown
            $propertyControl.find(".property-dropdown .down").html('&darr; results ' + (offset + limit + 1) + ' - ' + (offset + 2*limit));
            $propertyControl.find(".property-dropdown .down").show();
        } else {
            $propertyControl.find(".property-dropdown .down").hide();
        }
    };

    this.set_page = function(page) {

        if (page < 0) {
            page = 0;
        }
        this.page = page;

        this.show();
    };

    this.load(); //start loading properties

    var $propertyControl = $("#class_instance_" + this.c.id + " .property-control");

    $propertyControl.html('<input type="search" autocomplete="false" placeholder="find property"/><div class="dropdown-toggle-properties"><span class="loading"></span></div><span class="properties-found">Loading properties</span>');
    $propertyControl.append('<div class="property-dropdown"><div class="button up"></div><div class="properties-list"></div><div class="button down"></button></div>');

    /* Events */

    /* On toggle press */
    $propertyControl.find('.dropdown-toggle-properties').on('click', function(e) {
        var n = $(this).closest(".class-instance").data('n');
        if (that.qd.workbench.builder.instances[n].property_select.properties.length > 0) { //properties have loaded
            $('.class-instance:not(#class_instance_' + $(this).closest(".class-instance").data('n') + ') .property-dropdown').hide();
            $(this).parent().find(".property-dropdown").toggle();
            var _this = this;

            setTimeout( function() {$(_this).parent().find("input").focus()}, 100);

            e.preventDefault();
            e.stopPropagation();
        }
    });

    /* Don't hide the select on same input */
    $propertyControl.find('input').on('click', function(e) {
        $('.class-instance:not(#class_instance_' + $(this).closest(".class-instance").data('n') + ') .property-dropdown').hide();

        e.preventDefault();
        e.stopPropagation();
    });

    /* On filter */
    $propertyControl.find('input').on('input', function() {
        var n = $(this).parent().parent().parent().data('n');
        that.qd.workbench.builder.instances[n].property_select.set_page(0);
        $(this).parent().find('.property-dropdown').show();
    });


    /* prev & next property pages */
    $propertyControl.find('.property-dropdown > .up').on('click', function(e) {
        var n = $(this).closest(".class-instance").data('n');
        var p_select = that.qd.workbench.builder.instances[n].property_select;
        p_select.set_page(p_select.page - 1);

        e.preventDefault();
        e.stopPropagation();
    });

    $propertyControl.find('.property-dropdown > .down').on('click', function(e) {
        var n = $(this).closest(".class-instance").data('n');
        var p_select = that.qd.workbench.builder.instances[n].property_select;
        p_select.set_page(p_select.page + 1);

        //scroll back to top
        $(this).parent().animate({
            scrollTop: 0
        }, 300);

        e.preventDefault();
        e.stopPropagation();
    });

    /*Adding properties*/
    $propertyControl.on('click', '.properties-list .property', function(e) {
        var uri = $(this).data("uri");
        var n = $(this).closest(".class-instance").data('n');

        that.qd.workbench.builder.add_property(n, uri, $(this).text());
        that.qd.workbench.builder.reset();

        $(this).closest(".property-dropdown").toggle();

        //reset search
        $(this).closest(".property-dropdown").parent().find("input").val('');
        that.set_page(0);

        e.preventDefault();
        e.stopPropagation();
    });
};

$(function() {
    /* hide the select otherwise */
    $("body").on('click', function() {
        $(".property-dropdown").hide();
    });
})

