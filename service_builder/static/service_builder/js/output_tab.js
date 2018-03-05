$(document).ready(function(){

	// Base template
	var base_tpl =
			"<!doctype html>\n" +
			"<html>\n\t" +
      "<head>\n\t\t" +
      "<meta charset=\"utf-8\">\n\t\t" +
      "<title>Test</title>\n\n\t\t\n\t" +
      "</head>\n\t" +
      "<body>\n\t\n\t" +
      "</body>\n" +
      "</html>";

	var prepareSource = function() {
		var html = html_editor.getValue(),
            css = css_editor.getValue(),
			js = js_editor.getValue(),
			src = '';

		// HTML
		src = base_tpl.replace('</body>', html + '</body>');

		// CSS
		css = '<style>' + css + '</style>';
		src = src.replace('</head>', css + '</head>');

		// Javascript
		js = '<script>' + js + '<\/script>';
		src = src.replace('</body>', js + '</body>');

		return src;
	};

	var render = function() {
		var source = prepareSource();

		var iframe = document.querySelector('#output iframe'),
			iframe_doc = iframe.contentDocument;
		    // console.log(iframe_doc);

		iframe_doc.open();
		iframe_doc.write(source);
		iframe_doc.close();
	};


	// EDITORS

	// CM OPTIONS
	var cm_opt = {
		mode: 'text/html',
		gutter: true,
		lineNumbers: true,
        autoRefresh:true,
	};

	// HTML EDITOR
	var html_box = document.querySelector('#html textarea');
	var html_editor = CodeMirror.fromTextArea(html_box, cm_opt);

    html_editor.on('change', function (inst, changes) {
        render();
    });

	// CSS EDITOR
	cm_opt.mode = 'css';
	var css_box = document.querySelector('#css textarea');
	var css_editor = CodeMirror.fromTextArea(css_box, cm_opt);

    css_editor.on('change', function (inst, changes) {
        render();
    });

	// JAVASCRIPT EDITOR
	cm_opt.mode = 'javascript';
	var js_box = document.querySelector('#js textarea');
	var js_editor = CodeMirror.fromTextArea(js_box, cm_opt);

    js_editor.on('change', function (inst, changes) {
        render();
    });




	// RENDER CALL ON PAGE LOAD
	// NOT NEEDED ANYMORE, SINCE WE RELY
	// ON CODEMIRROR'S onChange OPTION THAT GETS
	// TRIGGERED ON setValue
	// render();


	// NOT SO IMPORTANT - IF YOU NEED TO DO THIS
	// THEN THIS SHOULD GO TO CSS

	/*
		Fixing the Height of CodeMirror.
		You might want to do this in CSS instead
		of JS and override the styles from the main
		codemirror.css
	*/
	var cms = document.querySelectorAll('.CodeMirror');
	for (var i = 0; i < cms.length; i++) {

		cms[i].style.position = 'absolute';
		cms[i].style.top = '30px';
		cms[i].style.bottom = '0';
		cms[i].style.left = '0';
		cms[i].style.right = '0';
        cms[i].style.height = '100%';
	}
	/*cms = document.querySelectorAll('.CodeMirror-scroll');
	for (i = 0; i < cms.length; i++) {
		cms[i].style.height = '100%';
	}*/

	// SETTING CODE EDITORS INITIAL CONTENT
	html_editor.setValue('<h1>Service 1</h1>');
	css_editor.setValue('h1 { color: blue; }');



//	END CODE MIRROR
// }());
//
// $(document).ready(function(){

    $('#addVizModal').on('show.bs.modal', function () {
        $('#load-viz-query-select').empty();
        $('#load-viz-query-select').append('<option disabled selected>-- select one of the loaded queries --</option>');
        $('#selected-queries-table tbody tr').each(function( index ) {
            $('#load-viz-query-select').append('<option  data-query-id="'+$( this ).children().eq(0).text()+'"> ' + $( this ).children().eq(1).text() + '-' + $( this ).children().eq(2).text() +' </option>');
        });
    });


	$('#addVizModal select').select2();


    function updateVariables(element) {
        $('#addVizModal .variable-select').find('option').remove().end();
        $('#addVizModal .variable-select').append($("<option disabled selected>-- select variable --</option>"));
        var new_query_id = $('#addVizModal #selected_query').val();
        var new_query_doc = {};
        $.ajax({
            url: '/queries/get_query_variables/',
            data: {
                id: new_query_id,
                document: new_query_doc
                },
            type: 'GET',
            success: function(result){
                var variables = result['variables'];
                var dimensions = result['dimensions'];
                $.each(variables, function(k, v) {
                    $('#addVizModal .variable-select').append($("<option></option>")
                        .attr("value", v)
                        .text(k));
                });

                $.each(dimensions, function(k, v) {
                    $('#addVizModal .variable-select').append($("<option></option>")
                        .attr("value", v)
                        .text(k));
                });
            }
        });
    }


    $('#addVizModal .select2').on("click", function() {
        $('.popover').popover('hide');
    });

    $('#addVizModal select').on('change', function() {
        $('#addVizModal #viz_config').show();
        var new_query_id = $(this).children(":selected").attr("data-query-id");
        $('#addVizModal #selected_query').val(new_query_id);
        $('.popover').popover('hide');
          // updateVariables(this);
    });



    $(".viz_item").click(function (element) {
      var component_id = $(this).attr('data-viz-id');
      var component_selector = 'li[data-viz-id="'+component_id+'"]';
      $.ajax({
            url: '/dashboards/get_visualization_form_fields',
            data: {
                id: parseInt(component_id),
                order: 1
                },
            type: 'GET',
            success: function(form_fields){
                $("#conf-container").html(form_fields);
                $("#conf-container").append('<button type="button" id="select_conf_ok" class="btn btn-sm btn-success" data-toggle="popover">OK</button>');

                $(component_selector).popover({
                    html: true,
                    title: 'Configure visualisation',
                    trigger: 'manual',
                    content: function() {
                        return $('#conf-container').html();
                    }
                });
                updateVariables($('#load-viz-query-select'));
                $(component_selector).popover('toggle');
                var popver_id = '#' + $(component_selector).attr('aria-describedby');
                $(popver_id+' #select_conf_ok').click(function(e){
                    submit_conf(component_selector);
                    $(component_selector).popover("hide");
                });
            }
        });
    });


    var viz_request = "";
    function submit_conf(component_selector) {
        viz_request = "http://localhost:8000/visualizations/";
        viz_request += $('#addVizModal').find('.modal-body').find('#action').val();
        var conf_popover_id = '#' + $(component_selector).attr('aria-describedby');

        var submitted_args = $('#addVizModal').find(conf_popover_id).find('.popover-content').clone();
        var selects = $('#addVizModal').find(conf_popover_id).find('.popover-content').find("select");
        $(selects).each(function(i) {
            var select = this;
            $(submitted_args).find("select").eq(i).val($(select).val());
        });
        $('#config-viz-form').empty();
        $('#config-viz-form').append(submitted_args);


        var myData = $("#config-viz-form").serialize();
        viz_request += '?';
        viz_request += myData;

        viz_request += '&query=' + $('#addVizModal #selected_query').val();

        show_viz(viz_request);
    }

    function show_viz(viz_request) {
        $("#viz_container").html('<iframe id="viz-iframe" ' +
            'src="'+viz_request+'" frameborder="0" allowfullscreen="" '+
            '></iframe>');
    }


    $("#addVizModal #submit-modal-btn").click(function () {
        $('#viz_container iframe').appendTo('#dynamic_dashboard');
        html_editor.replaceRange('\n<iframe src="'+viz_request+'" frameborder="0" allowfullscreen=""\n', {line: Infinity});
        html_editor.refresh();
        viz_request = "";
        $('#addVizModal #viz_container').empty();
    });
    $("#dismiss-modal-btn").click(function m (e) {
        viz_request = "";
        $('#addVizModal #viz_container').empty();
    });

}());
