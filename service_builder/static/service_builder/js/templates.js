$(".template_item").click(function () {
   var template_id = $(this).attr('data-template-id');
   $.ajax({
        "type": "GET",
        "url": "/service_builder/load_template/",
        "data": {
            template_id: template_id
        },
        "success": function(result) {
            // console.log(result);
            html_editor.setValue(result['html']);
            css_editor.setValue(result['css']);
	        js_editor.setValue(result['js']);
        },
        error: function (jqXHR) {
            alert('error');
        }
    });
});


function togglemask(show) {
  if(show)
    $('#service_container').append('<img id="loadergif" src="/static/img/loading_gif.gif" width="" height="">');
  else
    $('#service_container').find("#loadergif").remove();
}