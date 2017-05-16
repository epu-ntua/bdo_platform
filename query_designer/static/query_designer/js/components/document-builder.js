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
            .replace(/\./g, '_')
		    .replace(/\(/g, '_')
		    .replace(/\)/g, '_')
		    .replace(/%3A/g, '_')
            .toLowerCase();
    };

    // forges foreign key relationships
    this.createConnections = function(w) {
        var conns = qd.arrows.connections;

        for (var j=0; j<conns.length; j++) {
            var fn = conns[j].f.split('_')[2],
                tn = conns[j].t.split('_')[2]; //3rd part is the number #class_instance_1

            this.propertyNames[tn][conns[j].tp] = this.propertyNames[fn][conns[j].fp];
            w.instances[tn].selected_properties[conns[j].tp].name = this.propertyNames[tn][conns[j].tp];

            /*if (w.instances[tn].selected_properties[conns[j].tp].uri == "VALUE") {
                // if already renamed by another FK, we have a conflict we'll have to revisit
                if (typeof(this.instanceNames[tn].from) !== "undefined") {
                    this.conflicts.push({
                        instance: tn,
                        conflicting: {
                            instance: fn,
                            property: conns[j].fp
                        }
                    });
                } else {
                    this.instanceNames[tn].val = this.propertyNames[tn][conns[j].tp];
                    this.instanceNames[tn].from = {instance: tn, property: conns[j].tp};
                }
            }*/
        }
    };

    // resolve naming conflicts
    this.resolveConflicts = function(w) {
        for (var k=0; k<this.conflicts.length; k++) {
            var c = this.conflicts[k];

            var prevPropertyName = this.propertyNames[c.conflicting.instance][c.conflicting.property];
            var replaceWith = this.instanceNames[c.instance].val;
            for (var i=0; i<w.instances.length; i++) {
                for (var j=0; j<this.propertyNames[i].length; j++) {
                    if (this.propertyNames[i][j] == prevPropertyName) {
                        this.propertyNames[i][j] = replaceWith;
                    }
                }
            }
        }

        this.conflicts = [];
    };

    // find the names of the properties & forge foreign keys
    this.findPropertyNames = function(w, i) {
        var inst = w.instances[i];
        var i_name = this.instanceNames[i].val;

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

        // setup foreign key names
        this.conflicts = [];
        this.createConnections(w);

        // resolve any naming issue conflicts
        this.resolveConflicts(w);
    };

    this.getDocument = function() {
        return document;
    };

    // create document
    document = {
        from: [],
        offset: 0,
        limit: 100
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
            fromObject.select.push({
                type: property.uri,
                name: that.propertyNames[idx][jdx],
                title: property.label
            })
        });

        document.from.push(fromObject);
    });

    // add joins
    // TODO add joins

    // unpack
    that.qd.config.properties.unpack(document);

    return this;
};