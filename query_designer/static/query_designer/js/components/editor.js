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
				'<div class="panel panel-default editor-container" style="display: none;">' +
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

	this.setValue = function(newQuery) {
		editor.setValue(newQuery);
	};

	return this
};

