$(function() {
    var $modal = $('#select-data-modal');

     $(".dataset-section").click(function () {
         // Update the selection
         $(".dataset-section").not(this).attr("data-selected", "False");
         $(this).attr("data-selected", "True");

         var $datasetInfoDiv = $('#dataset_info_div');
         // Empty the previous info
         $datasetInfoDiv.find("#dataset_basic_info_div").empty();
         $datasetInfoDiv.find("#dataset-variables-div").empty();
         $datasetInfoDiv.find("#dataset-dimensions-div").empty();
         $datasetInfoDiv.find("#dataset-coverage-div").empty();
         $datasetInfoDiv.find("#dataset_metadata_div").empty();
         // Append the new dataset info
         $(this).find('.dataset-info .dataset-metadata').clone().appendTo($datasetInfoDiv.find("#dataset_metadata_div"));
         $(this).find('.dataset-info .dataset-variables-div').clone().appendTo($datasetInfoDiv.find("#dataset-variables-div"));
         $(this).find('.dataset-info .dataset-dimensions-div').clone().appendTo($datasetInfoDiv.find("#dataset-dimensions-div"));
         $(this).find('.dataset-info .dataset-coverage-div').clone().appendTo($datasetInfoDiv.find("#dataset-coverage-div"));
         $(this).find('.dataset-name').clone().appendTo($datasetInfoDiv.find("#dataset_basic_info_div"));

         $datasetInfoDiv.removeClass("hidden");

         // Mark as selected the variables that are already added to the Query Designer
         var included_vars = [];
         $.each(QueryToolbox.variables, function (_, variable) {
             included_vars.push(parseInt(variable.id));
         });
         $("#dataset-variables-div .variable-section").each(function (_, variable) {
             if(included_vars.indexOf($(variable).data('variable-id')) >= 0){
                 $(variable).attr({'data-selected': 'True'});
                 $(variable).attr({'data-disabled': 'True'});
             }
             else{
                 $(variable).attr({'data-selected': 'False'});
                 $(variable).attr({'data-disabled': 'False'});
             }
        });

        $("#dataset-variables-div").find('[data-toggle="tooltip"]').tooltip();
    });

   $('#dataset_info_div').on('click', ".variable-section[data-disabled='False']", function() {
       /* Select/Unselect variable */
       if($(this).attr('data-selected') === "False") {
           $(this).attr({'data-selected': 'True'});
       }
       else{
           $(this).attr({'data-selected': 'False'});
       }
       $(this).attr({'data-disabled': 'False'});

       if($("#dataset-variables-div .variable-section[data-selected='True'][data-disabled='False']").length > 0 ) {
           $('.selection-confirm').show();
       }
       else{
           $('.selection-confirm').hide();
       }

       window.getDataSelection = function() {
           var selection = [];
           $("#dataset-variables-div .variable-section[data-selected='True']").each(function (_, variable) {
               // Gather the dimensions of the selected variable
               var dims = [];
               $(this).find(".dimension-section span").each(function (_, dim) {
                   dims.push({
                        id: $(dim).data('type'),
                        name: $(dim).data('name'),
                        title: $(dim).data('title'),
                        datatype: $(dim).data('datatype')
                    })
               });
               selection.push({
                    id: $(variable).data('variable-id'),
                    name: $(variable).data('variable-name'),
                    title: $(variable).data('variable-title'),
                    unit: $(variable).data('variable-unit'),
                    datatype: $(variable).data('variable-datatype'),
                    dataset_id: $(variable).data('variable-dataset'),
                    dataset_size: $(variable).closest('#dataset_info_div').find("#dataset_metadata_div").find(".dataset-size").find("td").eq(1).text(),
                    dataset_name: $(variable).closest('#dataset_info_div').find("#dataset_basic_info_div").find(".dataset-title").text(),
                    dataset_lat_min: Math.floor(parseFloat($(variable).closest('#dataset_info_div').find("#dataset-coverage-div").find(".lat_from").text())),
                    dataset_lat_max: Math.ceil(parseFloat($(variable).closest('#dataset_info_div').find("#dataset-coverage-div").find(".lat_to").text())),
                    dataset_lon_min: Math.floor(parseFloat($(variable).closest('#dataset_info_div').find("#dataset-coverage-div").find(".lon_from").text())),
                    dataset_lon_max: Math.ceil(parseFloat($(variable).closest('#dataset_info_div').find("#dataset-coverage-div").find(".lon_to").text())),
                    dataset_time_min: $(variable).closest('#dataset_info_div').find("#dataset-coverage-div").find(".time_from").text(),
                    dataset_time_max: $(variable).closest('#dataset_info_div').find("#dataset-coverage-div").find(".time_to").text(),
                    aggregate: null,
                    groupBy: null,
                    dimensions: dims
                })
           });
           // console.log(selection);
           return selection;
       };
   });


    $(".jplist-reset-btn").click(function(){
        setTimeout(function(){$('#dataset-filter-section select').trigger("change");}, 100);
    });

    // $( function() {
    //     $( "#lat_range" ).slider({
    //         range: true,
    //         min: -90,
    //         max: 90,
    //         values: [ -90, 90 ],
    //         slide: function( event, ui ) {
    //             $( "#lat_range_begin" ).val(ui.values[0]);
    //             $( "#lat_range_end" ).val(ui.values[1]);
    //         }
    //     });
    //     $( "#lat_range_begin" ).val($( "#lat_range" ).slider( "values", 0 ));
    //     $( "#lat_range_end" ).val($( "#lat_range" ).slider( "values", 1 ));
    //
    //     $( "#lon_range" ).slider({
    //         range: true,
    //         min: -180,
    //         max: 180,
    //         values: [ -180, 180 ],
    //         slide: function( event, ui ) {
    //             $( "#lon_range_begin" ).val(ui.values[0]);
    //             $( "#lon_range_end" ).val(ui.values[1]);
    //         }
    //     });
    //     $( "#lon_range_begin" ).val($( "#lon_range" ).slider( "values", 0 ));
    //     $( "#lon_range_end" ).val($( "#lon_range" ).slider( "values", 1 ));
    // } );


    jQuery.fn.jplist.settings = {
        latSlider: function ($slider, $prev, $next){
         $slider.slider({
             min: -90
            ,max: 90
            ,range: true
            ,values: [-90, 90]
            ,slide: function (event, ui){
                $prev.text(ui.values[0]);
                $next.text(ui.values[1]);
                $("div[data-control-name='range-slider-lat-to']").find(".ui-slider").slider('values', 0, ui.values[0]);
                $("div[data-control-name='range-slider-lat-from']").find(".ui-slider").slider('values', 1, ui.values[1]);
            }
         });
      }
      ,latValues: function ($slider, $prev, $next){
         $prev.text($slider.slider('values', 0));
         $next.text($slider.slider('values', 1));
      }
      ,latSliderTo: function ($slider, $prev, $next){
         $slider.slider({
             min: -90
            ,max: 90
            ,range: true
            ,values: [-90, 90]
            ,slide: function (event, ui){
                $prev.text(ui.values[0]);
                $next.text(ui.values[1]);
                // $("div[data-control-name='range-slider-lat-from']").find(".ui-slider").slider('values', 0, parseInt($("div[data-control-name='range-slider-lat-to']").find(".value").eq(0).html()));
                // $("div[data-control-name='range-slider-lat-from']").find(".ui-slider").slider('values', 1, parseInt($("div[data-control-name='range-slider-lat-to']").find(".value").eq(1).html()));
            }
         });
      }
      ,latValuesTo: function ($slider, $prev, $next){
         $prev.text($slider.slider('values', 0));
         $next.text($slider.slider('values', 1));
      }
      ,latSliderFrom: function ($slider, $prev, $next){
         $slider.slider({
             min: -90
            ,max: 90
            ,range: true
            ,values: [-90, 90]
            ,slide: function (event, ui){
                $prev.text(ui.values[0]);
                $next.text(ui.values[1]);
             }
         });
      }
      ,latValuesFrom: function ($slider, $prev, $next){
         $prev.text($slider.slider('values', 0));
         $next.text($slider.slider('values', 1));
      }
      ,lonSlider: function ($slider, $prev, $next){
         $slider.slider({
             min: -180
            ,max: 180
            ,range: true
            ,values: [-180, 180]
            ,slide: function (event, ui){
                $prev.text(ui.values[0]);
                $next.text(ui.values[1]);
                $("div[data-control-name='range-slider-lon-to']").find(".ui-slider").slider('values', 0, ui.values[0]);
                $("div[data-control-name='range-slider-lon-from']").find(".ui-slider").slider('values', 1, ui.values[1]);
            }
         });
      }
      ,lonValues: function ($slider, $prev, $next){
         $prev.text($slider.slider('values', 0));
         $next.text($slider.slider('values', 1));
      }
      ,lonSliderTo: function ($slider, $prev, $next){
         $slider.slider({
             min: -180
            ,max: 180
            ,range: true
            ,values: [-180, 180]
            ,slide: function (event, ui){
                $prev.text(ui.values[0]);
                $next.text(ui.values[1]);
                // $("div[data-control-name='range-slider-lat-from']").find(".ui-slider").slider('values', 0, parseInt($("div[data-control-name='range-slider-lat-to']").find(".value").eq(0).html()));
                // $("div[data-control-name='range-slider-lat-from']").find(".ui-slider").slider('values', 1, parseInt($("div[data-control-name='range-slider-lat-to']").find(".value").eq(1).html()));
            }
         });
      }
      ,lonValuesTo: function ($slider, $prev, $next){
         $prev.text($slider.slider('values', 0));
         $next.text($slider.slider('values', 1));
      }
      ,lonSliderFrom: function ($slider, $prev, $next){
         $slider.slider({
             min: -180
            ,max: 180
            ,range: true
            ,values: [-180, 180]
            ,slide: function (event, ui){
                $prev.text(ui.values[0]);
                $next.text(ui.values[1]);
             }
         });
      }
      ,lonValuesFrom: function ($slider, $prev, $next){
         $prev.text($slider.slider('values', 0));
         $next.text($slider.slider('values', 1));
      }
      ,timeSlider: function ($slider, $prev, $next){
         $slider.slider({
             min: time_start_timestamp
            ,max: time_end_timestamp
            ,range: true
            ,values: [time_start_timestamp, time_end_timestamp]
            ,slide: function (event, ui){
                 // $prev.text(ui.values[0]);
                // $next.text(ui.values[1]);
                var start_date = new Date(ui.values[0]);
                var end_date = new Date(ui.values[1]);
                $prev.text(start_date.getFullYear() + "/" + (start_date.getMonth()+1) + "/" + start_date.getDate());
                $next.text(end_date.getFullYear() + "/" + (end_date.getMonth()+1) + "/" + end_date.getDate());
                $("div[data-control-name='range-slider-time-to']").find(".ui-slider").slider('values', 0, ui.values[0]);
                $("div[data-control-name='range-slider-time-from']").find(".ui-slider").slider('values', 1, ui.values[1]);
            }
         });
      }
      ,timeValues: function ($slider, $prev, $next){
          // $prev.text($slider.slider('values', 0));
         // $next.text($slider.slider('values', 1));
         var start_date = new Date($slider.slider('values', 0));
         var end_date = new Date($slider.slider('values', 1));
         $prev.text(start_date.getFullYear() + "/" + (start_date.getMonth()+1) + "/" + start_date.getDate());
         $next.text(end_date.getFullYear() + "/" + (end_date.getMonth()+1) + "/" + end_date.getDate());
      }
      ,timeSliderTo: function ($slider, $prev, $next){
         $slider.slider({
             min: time_start_timestamp
            ,max: time_end_timestamp
            ,range: true
            ,values: [time_start_timestamp, time_end_timestamp]
            ,slide: function (event, ui){
                 // $prev.text(ui.values[0]);
                // $next.text(ui.values[1]);
                var start_date = new Date(ui.values[0]);
                var end_date = new Date(ui.values[1]);
                $prev.text(start_date.getFullYear() + "/" + (start_date.getMonth()+1) + "/" + start_date.getDate());
                $next.text(end_date.getFullYear() + "/" + (end_date.getMonth()+1) + "/" + end_date.getDate());
            }
         });
      }
      ,timeValuesTo: function ($slider, $prev, $next){
          // $prev.text($slider.slider('values', 0));
         // $next.text($slider.slider('values', 1));
         var start_date = new Date($slider.slider('values', 0));
         var end_date = new Date($slider.slider('values', 1));
         $prev.text(start_date.getFullYear() + "/" + (start_date.getMonth()+1) + "/" + start_date.getDate());
         $next.text(end_date.getFullYear() + "/" + (end_date.getMonth()+1) + "/" + end_date.getDate());
      }
      ,timeSliderFrom: function ($slider, $prev, $next){
         $slider.slider({
             min: time_start_timestamp
            ,max: time_end_timestamp
            ,range: true
            ,values: [time_start_timestamp, time_end_timestamp]
            ,slide: function (event, ui){
                 // $prev.text(ui.values[0]);
                // $next.text(ui.values[1]);
                var start_date = new Date(ui.values[0]);
                var end_date = new Date(ui.values[1]);
                $prev.text(start_date.getFullYear() + "/" + (start_date.getMonth()+1) + "/" + start_date.getDate());
                $next.text(end_date.getFullYear() + "/" + (end_date.getMonth()+1) + "/" + end_date.getDate());
             }
         });
      }
      ,timeValuesFrom: function ($slider, $prev, $next){
          // $prev.text($slider.slider('values', 0));
         // $next.text($slider.slider('values', 1));
         var start_date = new Date($slider.slider('values', 0));
         var end_date = new Date($slider.slider('values', 1));
         $prev.text(start_date.getFullYear() + "/" + (start_date.getMonth()+1) + "/" + start_date.getDate());
         $next.text(end_date.getFullYear() + "/" + (end_date.getMonth()+1) + "/" + end_date.getDate());
      }
     };
});