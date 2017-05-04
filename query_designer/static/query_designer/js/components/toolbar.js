/**
 * Created by dimitris on 4/5/2017.
 */
var Toolbar = function(qd) {
    var that = this;

    this.allClassesProperties = [];
    this.classesQueryPaginateBy = 10000;
    this.nOfEmpty = 0;

    this.qd = qd;
    this.config = qd.config.toolbar;

    var $toolbar = this.qd.$container.find('.toolbar');

    this.clear = function() {
        this.allClassesProperties = [];
        this.labels = [];
    };

    this.loadClasses = function(p) {
        var datasetId = that.qd.datasetSelect.getDatasetId(),
            url = that.config.classesSource.from.replace('{{ datasetId }}', datasetId).replace('{{ p }}', p);

        $.ajax({ //make request for classes
            url: url,
            type: "GET",
            success: function(classes) {
                if (p === 1) {
                    if (that.startedLoading) { //loading has already started
                        return;
                    }

                    that.startedLoading = true;
                    that.nOfEmpty = 0;
                }

                $.each(classes, function(idx, _class) {
                    that.allClassesProperties.push({type: "class", item: _class});
                });

                if (classes.length == that.classesQueryPaginateBy) { //continue gathering classes
                    that.loadClasses(p + 1);
                }

                //show changes
                setTimeout(function() {
                    var val = $toolbar.find('input[type="search"]' ).val();
                    if (val === undefined) {
                        val = "";
                    }
                    that.showClasses(val, undefined, true);
                }, 10);
            },
            error: function (jqXHR, textStatus, errorThrown) {
                console.log(textStatus + ': ' + errorThrown);
                return -1;
            }

        });
    };

    this.showClasses = function(filter, offset, appending) {
        var limit = 10;
        var added = 0;
        var total = 0;
        var start = 0;
        var isFull = false;

        if (appending) { //used to optimize loading large data sources
            isFull = $toolbar.find('.active-classes .button').length == limit;
            if ((this.prevState) && (filter == this.prevState.filter)) {
                start = this.prevState.len;
                added = this.prevState.added;
                total = this.prevState.total;
                offset = this.prevState.offset;
            } else {
               $toolbar.find('.active-classes').empty();
            }
        } else {
            $toolbar.find('.active-classes').empty();
            if ((this.prevState != undefined) && (filter == this.prevState.filter)) {
                var prevTotal = this.prevState.total;
            }
            this.prevState = undefined;
        }

        if (offset === undefined) {
            offset = 0;
        }

        if ((offset > 0) && (this.prevState === undefined)) {
            $toolbar.find('.active-classes').append('<span class="prev-next-classes-button" data-offset="' + (Math.max(offset-limit, 0)) + '">‹</span>');
        }

        if (this.prevState === undefined) {
            $toolbar.find('.active-classes').append('<div class="classes-container" />');
        }

        for (var i=start; i<this.allClassesProperties.length; i++) {
            if (!filter || (this.allClassesProperties[i].item.title.toLowerCase().indexOf(filter.toLowerCase()) >= 0)) {
                total++;
                if ((total > offset) && (total <= offset + limit)) {
                    if (!isFull) {
                        var typeClass = this.allClassesProperties[i].type;
                        var dataStr = 'data-id="' + this.allClassesProperties[i].item._id + '" data-type="' + typeClass+ '"';
                        var newButton = '<div class="class_button button btn btn-sm ' + typeClass + '" ' + dataStr + '>' + this.allClassesProperties[i].item.title + '</div>';
                        $toolbar.find('.active-classes .classes-container').append(newButton);
                    }

                    added++;
                }
                else if ((prevTotal != undefined) && (total > offset)) {
                    //total already known so we may break;
                    total = prevTotal;
                    break;
                }
            }
        }

        if (!isFull) {
            if ((offset + added < total) && ($toolbar.find('.active-classes .prev-next-classes-button').length < 2)) {
                $toolbar.find('.active-classes').append('<span class="prev-next-classes-button" data-offset="' + (offset+limit) + '">›</span>');
            }
        }

        if ((added == 0) && (this.prevState == undefined)) {
            $toolbar.find('.active-classes').append('<span class="info">No terms found</span>');
        } else if (this.allClassesProperties.length>limit) {
            var info_str = 'Showing ' + (offset+1) + '-' + (offset+added) + '/' + total.toLocaleString() + ' terms';
            if (this.prev_state !== undefined) {
                $toolbar.find('active-classes .info').html(info_str);
            } else {
                $toolbar.find('.active-classes').append('<span class="info">' + info_str + '</span>');
            }

            if (that.finishedLoading) {
                $toolbar.find('.active-classes .info').removeClass('loading');
            } else {
                $toolbar.find('.active-classes .info').addClass('loading');
            }
        }

        //store the state to change pages faster
        this.prev_state = {
            total: total,
            added: added,
            len: this.allClassesProperties.length,
            filter: filter,
            offset: offset
        };

        // $("#tree_toolbar").css('top', $(".toolbar-container").position().top + $(".toolbar-container").height() + 10);
    };

    this.onDatasetSelect = function() {
        that.startedLoading = false;
        that.finishedLoading = false;

        update_tree_toolbar();

        $toolbar.find('.active-classes').html('<span class="loading">Loading items...</span>');
        // $("#tree_toolbar").css('top', $(".toolbar-container").position().top + $(".toolbar-container").height() + 10);

        that.clear();

        // load first page of classes
        setTimeout(function() {
            that.loadClasses(1);

            // create a worker to show classes
            if (window.Worker) {
                that.order_worker = new Worker("/static/query_designer/js/util/on-worker-message.js");
                that.order_worker.onmessage = function(e) {
                    that.allClassesProperties = e.data;
                    that.showClasses($toolbar.find('> input[type="search"]' ).val());
                    $toolbar.css('cursor', 'default');
                };
            }
        }, 500);
    };

    /* Events */

    // On dataset select change
    $toolbar.find('select').on('change', function() {
        that.onDatasetSelect();
    });

    // On search text change
    $toolbar.find('> input[type="search"]' ).on('input propertychange paste', function() {
        var $search = $(this),
            term = $search.val();

        setTimeout(function(){
            if (term === $search.val()) { // input value has not changed
                that.showClasses(term);
            }
        }, 250);

    });

    // on class start drag
    $("body").on('mousedown','.class_button', function(e) {
        if (e.which == 1) { // only for left click
            that.qd.workbench.selection = {'type': $(this).data("type"), 'uri': $(this).data("uri"), 'dt_name': $toolbar.find(' > select').val()};
            if ($(this).data("type") == "property") {
                that.qd.workbench.builder.selection.domain = $(this).data("domain");
                that.qd.workbench.builder.selection.range = $(this).data("range");
            }

            $toolbar.addClass("accepting-instance");
            e.preventDefault();
            e.stopPropagation();
        }
    });

    // on class cancel drag
    $("body").on('mouseup','.toolbar', function(e) {
        that.qd.workbench.builder.selection = undefined;
    });

    // On toolbar prev & next
    $toolbar.on('click','.prev-next-classes-button', function() {
        var offset = $(this).data('offset');
        that.showClasses($toolbar.find(' > input[type="search"]').val(), offset);
    });
};


function update_tree_toolbar() {
    return;

    var name = $( "#toolbar > select" ).val();
    var that = $( "#toolbar > select" );
    if (name == "") return;

    TreeObjects = [];
    $('#tree_toolbar_objects').empty();
    that.prev_state = undefined;

    $.ajax({ //make request for classes
        url: ADVANCED_BUILDER_API_URI + "active_root_classes/" +  name + "/",
        type: "GET",

        success: function(data, textStatus, jqXHR) {
            if ($(that).val() != name) { //changed
                return;
            }
            var bindings = data.results.bindings;

            for (var i=0; i<bindings.length; i++) { //add all classes
                var class_uri = bindings[i].class.value;
                var instance_cnt = bindings[i].cnt.value;

                var id = 'tree_class_' + i;
                var text = uri_to_label(class_uri) + ' (' + Number(instance_cnt).toLocaleString() + ')';
                $("#tree_toolbar_objects").append('<div id="' + id + '" class="class-wrapper"><span class="ui-icon ui-icon-carat-1-e arrow closed unset"></span><span class="class">' + text + '</span></div>');
                TreeObjects[id] = encodeURIComponent(class_uri);
            }
        },
        error: function (jqXHR, textStatus, errorThrown) {
            console.log(textStatus + ': ' + errorThrown);
        }
    });
}

/*Open a class*/
$("#tree_toolbar").on('click', '.arrow.closed', function(e) {
    $(this).removeClass('closed');
    $(this).addClass('open');

    $(this).removeClass('ui-icon-carat-1-e');
    $(this).addClass('ui-icon-carat-1-s');

    $(this).parent().find(".class-contents").show();
});

/*Close a class*/
$("#tree_toolbar").on('click', '.arrow.open', function(e) {
    $(this).removeClass('open');
    $(this).addClass('closed');

    $(this).removeClass('ui-icon-carat-1-s');
    $(this).addClass('ui-icon-carat-1-e');

    $(this).parent().find(".class-contents").hide();
});

/*Dynamically load subclasses and properties*/
$("#tree_toolbar").on('click', '.arrow.closed.unset', function(e) {
    var parent_id = $(this).parent().attr('id');
    var parent_uri = TreeObjects[parent_id];

    $(this).removeClass('unset');
    $(this).addClass('loading');
    var arrow = $(this);

    $(this).parent().append('<div class="class-contents"></div>');
    var container = $(this).parent().find(".class-contents");

    $.ajax({ //make request for subclasses
        url: ADVANCED_BUILDER_API_URI + "active_subclasses/" +  $( "#toolbar > select" ).val() + "/?parent_class=" + parent_uri,
        type: "GET",

        success: function(data, textStatus, jqXHR) {
            var bindings = data.results.bindings;
            var nOfSubclasses = 0;
            for (var i=0; i<bindings.length; i++) { //add all classes
                if (!bindings[i].class) continue;

                nOfSubclasses++;
                var class_uri = bindings[i].class.value;
                var instance_cnt = bindings[i].cnt.value;

                var id = parent_id + '_tree_class_' + i;
                var text = uri_to_label(class_uri) + ' (' + Number(instance_cnt).toLocaleString() + ')';
                $(container).append('<div id="' + id + '"><span class="ui-icon ui-icon-carat-1-e arrow closed unset"></span><span class="class">' + text + '</span></div>');
                TreeObjects[id] = encodeURIComponent(class_uri);
            }

            arrow.removeClass('loading');
            if (nOfSubclasses == 0) {
                arrow.addClass('ui-icon-minus');
            }
        },
        error: function (jqXHR, textStatus, errorThrown) {
            arrow.removeClass('loading');
            arrow.removeClass('ui-icon-carat-1-s');
            arrow.addClass('ui-icon-carat-1-e');
            arrow.addClass('unset');

            console.log(textStatus + ': ' + errorThrown);
        }
    });
});

/*On class start drag*/
$("body").on('mousedown','#tree_toolbar .class', function(e) {
    if (e.which == 1) { //only for left click
        var class_uri = decodeURIComponent(TreeObjects[ $(this).parent().attr("id") ]);
        builder_workbench.selection = {'type': 'class', 'uri': class_uri, 'dt_name': $( "#toolbar > select" ).val()};
        $("#tree_toolbar").addClass("accepting-instance");

        e.preventDefault();
        e.stopPropagation();
    }
});

/*On class cancel drag*/
$("body").on('mouseup','#tree_toolbar', function(e) {
    builder_workbench.selection = undefined;
});

/*On tree toolbar close*/
$("body").on('click', '.tree-toolbar-close', function(e) {
    $("#tree_toolbar").css('max-width', 20);

    $(this).removeClass('tree-toolbar-close');
    $(this).addClass('tree-toolbar-open');

    $(this).removeClass('ui-icon-triangle-1-e');
    $(this).addClass('ui-icon-triangle-1-w');

    $('#tree_toolbar_objects').hide();
    e.preventDefault();
    e.stopPropagation();
});

/*On tree toolbar open*/
$("body").on('click', '.tree-toolbar-open', function(e) {
    $("#tree_toolbar").css('max-width', 300);

    $(this).removeClass('tree-toolbar-open');
    $(this).addClass('tree-toolbar-close');

    $(this).removeClass('ui-icon-triangle-1-w');
    $(this).addClass('ui-icon-triangle-1-e');

    $('#tree_toolbar_objects').show();
    e.preventDefault();
    e.stopPropagation();
});

$("body").on('dblclick', '.tree-toolbar-close, .tree-toolbar-open', function(e) {
    e.preventDefault();
    e.stopPropagation();
});
