 var numOfNodes;
 var analysis_flow = {};
 var newOutputColumns = [];
 var x = 0;
 var y = -200;

 // create an array with nodes
 var nodes = new vis.DataSet([]);

 // create an array with edges
 var edges = new vis.DataSet();

 // create a network
 var container = document.getElementById('dynamic_service');
 var data = {
     nodes: nodes,
     edges: edges
 };
 var options = {
     physics: {
         enabled: false
     }
 };
 $('document').ready(function(){
     load_map();
     var network = new vis.Network(container, data, options);
     numOfNodes = 0;
     nodes.add({
         id: 0,
         label: "Start",
         x: x,
         y: y
     })
 });

 $('.addNodeBtn').on('click', function() {
     y += 70;
     nodes.add({
         id: numOfNodes+1,
         label: this.getAttribute("data-component-title"),
         shape: 'box',
         widthConstraint: {
             minimum: 50
         },
         x: x,
         y: y
     });

     edges.add({
         id: numOfNodes+1,
         from: numOfNodes,
         to: numOfNodes+1,
         arrows:'to'
     });

     numOfNodes++;
     add_analysis_form_fields(this);

 });


 $('#myModal').on('hide.bs.modal', function(e){
            move_map("#mapframe","#hiddenelement");
        });
 $( '#myModal' ).on('shown.bs.modal', function(e){
     move_map("#mapframe","#newmap");
 });



 $('#submit-args-btn').on('click', function() {
    var submitted_args = $('#myModal').find('.modal-body').clone();
    var selects = $('#myModal').find('.modal-body').find("select");
    $(selects).each(function(i) {
        var select = this;
        $(submitted_args).find("select").eq(i).val($(select).val());
    });

    var newOutputCols = $(submitted_args).find("input[name*='outputCol']");
    $(newOutputCols).each(function(i) {
        newOutputColumns.push($(this).val()+' (derived)');
        $(submitted_args).find("input[name*='outputCol']").eq(i).val($(this).val()+' (derived)');
    });


    $('#config-service-form').append(submitted_args);

    var component_id = $('#myModal').find('input[name="anal_id"]').val();
    updateAnalysisFlow(component_id);
 });

 $('#dismiss-args-btn').on('click', function() {
     edges.remove(numOfNodes);
     nodes.remove(numOfNodes);
     y -= 70;
     numOfNodes--;
 });

 $('#removeLastBtn').on('click', function(){
     if(numOfNodes>0) {
         edges.remove(numOfNodes);
         nodes.remove(numOfNodes);
         y -= 70;
         var findStr = numOfNodes + "+++fieldset";
         var results = $('#config-service-form').find('fieldset');

         $(results).each(function () {
             if (this.getAttribute("name") == findStr) {
                 $(this).remove();
             }
         });
         delete analysis_flow[numOfNodes];
         $('#analysis_flow').val(JSON.stringify(analysis_flow));
         numOfNodes--;
     }
 })


 $('#query-select').on('change', function() {
     updateVariables(this);
     addQueryToForm(this.options[this.selectedIndex].value.replace(/\n/g, " "));
// {#          TODO: JOHN, when the query is changed all the service must be reset!#}
 });


  $('a#new_query_link').click(function(){
      var left  = ($(window).width()/2)-(900/2);
      var top   = ($(window).height()/2)-(600/2);
      window.open('/queries/', 'window name', 'width=900, height=600, top='+top+', left='+left);
      return false;
  });





 function add_analysis_form_fields(element) {
     var component_id = element.getAttribute('data-component-id');
     $.ajax({
         url: '/analytics/get-analysis-form-fields/',
         data: {
             id: parseInt(component_id),
             order: numOfNodes
         },
         type: 'GET',
         success: function(form_fields){
             $('#myModal').find('.modal-body').html(form_fields);
             $('#myModal').find('h5').html(element.getAttribute('data-component-title'));
             updateVariables($('#query-select'));
             $( "#modalbtn" ).trigger( "click" );
         }
     });
 }




 function updateAnalysisFlow(component_id) {
     analysis_flow[numOfNodes.toString()] = component_id;
     $('#analysis_flow').val(JSON.stringify(analysis_flow));
 }



 function updateVariables(element) {
     $('#myModal .variable-select').find('option').remove().end();
     $('#myModal .variable-select').append($("<option disabled selected>-- select variable --</option>"));
     var new_query_id = $(element).children(":selected").attr("id");
     var new_query_doc = $('#new_query_doc').val();
     $.ajax({
         url: '/queries/get_query_variables/',
         data: {
             id: new_query_id,
             document: new_query_doc
         },
         type: 'GET',
         success: function(variables){
             $.each(variables['variables'], function(k, v) {
                 $('#myModal .variable-select').append($("<option></option>")
                     .attr("value", v)
                     .text(k));
             });
             $.each(newOutputColumns, function() {
                 $('#myModal .variable-select').append($("<option></option>")
                     .attr("value", this)
                     .text(this));
             });
         }
     });
 }

 function addQueryToForm(raw_query){
     $('#config-service-form #query').val(raw_query);
 }


 function addNewQuery(title, raw_query, document) {
     $("#query-select option[id='-1']").remove().end();
     $('#query-select').append($("<option selected id='-1' value='" + raw_query + "'>" + title + "</option>"));
     $('#new_query_doc').val(document);
     updateVariables($('#query-select'));
     addQueryToForm(raw_query)
 }