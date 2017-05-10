/**
 * Created by dimitris on 10/5/2017.
 */
QueryEditor = function(qd) {
	var that = this;
	this.qd = qd;

	this.ui = {
		$elem: undefined,

		render: function() {
			this.$elem = $(
				'<div class="panel panel-default editor-container">' +
					'<div class="panel-heading">' +
						'<div class="row">' +
							'<div class="col-md-6">' +
								'<h4>Equivalent Query</h4>' +
							'</div>' +
						'</div>' +
					'</div>' +
					'<div class="panel-body" >' +
						'<div class="row">' +
							'<div class="col-md-12">' +
								'<div id="raw-query-editor"></div>' +
							'</div>' +
						'</div>' +
					'</div>' +
				'</div>'
			);

			// add to query designer
			that.qd.$container.append(this.$elem);
		}
	};

	// render
	this.ui.render();

	// initial editor configuration
	var editor = ace.edit('raw-query-editor');
	editor.setTheme("ace/theme/monokai");
	editor.setShowPrintMargin(false);
	editor.setOptions({
		readOnly: true
	});
	editor.getSession().setUseWrapMode(true);
	editor.$blockScrolling = Infinity;

	var SparqlMode = require("ace/mode/" + qd.config.language.mode).Mode;
	editor.getSession().setMode(new SparqlMode());

	/*F9 to run query*/
	$("body").on('keyup', function(e) {
    	if (e.keyCode == 120) { //F9 key pressed
    		if ($(".designer-button.run-button").length > 0) {
    			$(".designer-button.run-button").click();
    		} else {
    			execute_sparql_query();
    		}
        }
    });

    /*Ctrl+S to save query*/
	document.addEventListener("keydown", function(e) {
    	if (e.keyCode == 83 && e.ctrlKey) { //Ctrl+S key pressed
        	if (typeof(builder_workbench) === "undefined") {
        		save_query();
        	} else {
        		save_design();
        	}

			e.preventDefault();
			e.stopPropagation();
        }
    }, false);

	this.setValue = function(newQuery) {
		editor.setValue(newQuery);
	};

	return this
};

