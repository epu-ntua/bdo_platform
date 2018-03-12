$(document).ready(function(){

    $('.alert-success').fadeOut(5000);

    /*$('#dataset-dropdown').on('change', function(e){
        var selected = $(this).find(":selected").val();
        console.log(selected);
    });*/

    $('#file-upload-radio').on('change', function () {
        // console.log('Upload');
        $('#file-download-radio').prop('checked', false);
        $('#file-upload-picker').prop('disabled', false);
        $('#file-download-url').prop('disabled', true);
        $('#file-download-name').prop('disabled', true);
    });

    $('#file-download-radio').on('change', function () {
        // console.log('Download');
        $('#file-upload-radio').prop('checked', false);
        $('#file-upload-picker').prop('disabled', true).val('');
        $('#file-download-url').prop('disabled', false);
        $('#file-download-name').prop('disabled', false);
    });
});