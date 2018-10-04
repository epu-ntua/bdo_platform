$(document).ready(function(){
    $("#profile-dropdown").select2({width: '50%'});

    $('.alert').fadeOut(10000);


    $('#upload_pill').on('click', function () {
        // console.log('Upload');
        $('#file-download-radio').prop('checked', false);
        $('#file-upload-radio').prop('checked', true);
        $('#file-upload-picker').prop('disabled', false);
        $('#file-download-method').prop('disabled', true);
        $('#file-download-url').prop('disabled', true);
        $('#file-download-directory').prop('disabled', true);
        $('#file-download-name').prop('disabled', true);
        $('#file-download-username').prop('disabled', true);
        $('#file-download-password').prop('disabled', true);
        $("#profile-dropdown option").first().prop('selected', true).change();
    });

    $('#download_pill').on('click', function () {
        // console.log('Download');
        $('#file-upload-radio').prop('checked', false);
        $('#file-download-radio').prop('checked', true);
        $('#file-upload-picker').prop('disabled', true).val('');
        $('#file-download-method').prop('disabled', false);
        $('#file-download-url').prop('disabled', false);
        $('#file-download-directory').prop('disabled', false);
        $('#file-download-name').prop('disabled', false);
        $('#file-download-username').prop('disabled', false);
        $('#file-download-password').prop('disabled', false);
        $("#profile-dropdown option").first().prop('selected', true).change();
    });


    // $('#demo').steps({
    //     showBackButton: function () { alert('complete'); }
    // });
});