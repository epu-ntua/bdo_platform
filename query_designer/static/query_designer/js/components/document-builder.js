/**
 * Created by dimitris on 10/5/2017.
 */
DocumentBuilder = function(qd) {
    var that = this;

    this.qd = qd;
    var document = null;

    this.propertyNames = [];
    this.instanceNames = [];

    var slugify = function(title) {
        return title
            .replace(/ /g, '_')
            .replace(/-/g, '_')
            .replace(/,/g, '_')
            .replace(/\//g, '_')
            .replace(/\+/g, '_')
            .replace(/-/g, '_')
            .replace(/\\/g, '_')
            .replace(/\./g, '_')
		    .replace(/\(/g, '_')
		    .replace(/\)/g, '_')
		    .replace(/%3A/g, '_')
            .toLowerCase();
    };

    // find the names of the properties & forge foreign keys
    this.findPropertyNames = function(w, i) {
        var inst = w.instances[i];
        var i_name = 'i' + i; // this.instanceNames[i].val;

        for (var j=0; j<inst.selected_properties.length; j++) {
            var p = inst.selected_properties[j];
            if (this.instanceNames[i][j] === undefined) {
                if (p.name === undefined || !p.name_from_user) {
                    p.name = i_name + '_' + slugify(p.label);
                    p.name_from_user = false;
                    p.instance = inst;
                }

                this.propertyNames[i][j] = p.name;
            }
        }
    };

    // finds instance & property names
    this.findNames = function(w) {
        var i_names = this.instanceNames;

        // initialize base unique names to empty
        for (var i=0; i<w.instances.length; i++) {
            var p = w.instances[i].label;
            if (p !== undefined) {
                if (p.name !== undefined  && p.name != "" && p.name_from_user) {
                    i_names[i] = {val: p.name};
                } else {
                    i_names[i] = {val: ""};
                }
            }
        }

        // set base unique names
        for (var i=0; i<w.instances.length; i++) {
            var p_uri = w.instances[i].uri;
            if ((p_uri.name_from_user) || (i_names[i].val != "")) continue;

            var label = slugify(w.instances[i].label);

            var cnt = 1; //label is found once
            for (var j=i+1; j<w.instances.length; j++) {  //search if there are class instances with the same label
                if ((w.instances[j].label == w.instances[i].label) && (w.instances[j].subquery === w.instances[i].subquery)) {
                    if (i_names[i].val == "") {
                        i_names[i].val = label + '1';
                    }

                    cnt++;
                    i_names[j].val = label + cnt;
                }
            }

            if (i_names[i].val == "") {
                i_names[i].val = label;
            }
            p_uri.name = i_names[i].val;
        }

        // find property names
        for (var i=0; i<w.instances.length; i++) {
            this.propertyNames[i] = [];
        }

        for (var i=0; i<w.instances.length; i++) {
            this.findPropertyNames(w, i);
        }
    };

    this.getDocument = function() {
        return document;
    };

    // create document
    document = {
        from: [],
        distinct: that.qd.options.isDistinct(),
        filters: undefined,
        offset: that.qd.options.getOffset(),
        limit: that.qd.options.getLimit()
    };

    // find instance & property names
    this.findNames(qd.workbench.builder);

    // add properties to select & add instances to from
    $.each(qd.workbench.builder.instances, function(idx, instance) {
        var fromObject = {
            type: instance.uri,
            name: that.instanceNames[idx].val,
            select: []
        };

        $.each(instance.selected_properties, function(jdx, property) {
            var prop = {
                type: property.uri,
                name: that.propertyNames[idx][jdx],
                title: property.label
            };

            $.each(qd.arrows.connections, function(_, connection) {
                var tIdx = Number(connection.t.split('_')[2]);
                if ((tIdx === idx) && (jdx === connection.tp)) {
                    prop.joined = that.propertyNames[connection.f.split('_')[2]][connection.fp];
                }
            });

            fromObject.select.push(prop);
        });

        document.from.push(fromObject);
    });

    // add filters
    $.each(qd.workbench.builder.instances, function(idx, instance) {
        $.each(instance.selected_properties, function (jdx, property) {
            if (property.filters.length > 0) {
                var filterStr = property.filter_prototype,
                    name = that.propertyNames[idx][jdx];

                filterStr = filterStr
                    .replace(/\[/g, '{')
                    .replace(/\]/g, '}');

                for (var fId = 0; fId < property.filters.length; fId++) {
                    var f = property.filters[fId];
                    filterStr = filterStr.replace('{' + fId + '}',
                        '{"a": "' + name + '", "op": "' + f.operator + '", "b": "' + f.value + '"}');
                }

                filterStr = filterStr
                    .replace(/\(/g, '{')
                    .replace(/\)/g, '}')
                    .replace(/\s/g, '')
                    .replace(/&&\{/g, ', "op": "AND", "b": {')
                    .replace(/\|\|\{/g, ', "op": "OR", "b": {');

                if (property.filters.length > 1) {
                    filterStr = '{"a":' + filterStr + '}'
                }

                if (document.filters === undefined) {
                    document.filters = JSON.parse(filterStr);
                } else {
                    document.filters = {
                        "a": JSON.parse(JSON.stringify(document.filters)),
                        "op": "AND",
                        "b": JSON.parse(filterStr)
                    }
                }
            }
        });
    });

    // add joins
    // TODO add joins

    // unpack
    that.qd.config.properties.unpack(document);

    return this;
};