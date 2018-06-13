$(document).ready(function() {

    /*          Set Up Time Pickers For Start/End Date  */
    $('.date').datetimepicker({autoclose: true, pickerPosition: 'top-right'});

    // startpick.on('changeDate', function(e){
    //     var minDate = new Date(e.date.valueOf());
    //     endpick.datetimepicker('setStartDate' ,minDate);
    //     startdate = $('#startdatepicker input').val();
    //     // set_time_filters();
    // });
    // endpick.on('changeDate', function(e){
    //     var maxDate = new Date(e.date.valueOf());
    //     startpick.datetimepicker('setEndDate', maxDate);
    //     enddate = $('#enddatepicker input').val();
    //     // set_time_filters();
    // });
    /*          Set Up Time Pickers For Start/End Date  */



    // $('#project').on('click', function(){
    //     console.log(startdate, enddate);
    //     // startdate and enddate must be transposed to match database format
    //     QueryToolbox.filterManager.addFilter('timestamp', 'gt' , startdate.toString());
    //     QueryToolbox.filterManager.addFilter('timestamp', 'lt' , enddate.toString());
    // });


    // function set_time_filters() {
    //     var time_dim_id = $('#selected_dimensions option[data-type="time"]').val();
    //
    // }


});

$('.coverage-date-filters').ready(function() {
    $('.coverage-date-filters').parent().find('label').css({'left': '0'})
});
