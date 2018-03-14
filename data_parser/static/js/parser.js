$(document).ready(function(){

    $('.alert').fadeOut(10000);

    $('#provider-dropdown').on('change', function() {
        var selected = $(this).find(":selected").val();

        $.ajax({
            async: true,
            crossDomain: true,
            url: "http://212.101.173.34:8085/file/parsable/" + selected,
            // url: "http://127.0.0.1/file/parsable/" + selected,
            method: "GET",
            headers: {
                Authorization: "Bearer eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJiZG8iLCJleHAiOjE1NTE4Njg4MzUsInJvbGUiOiJST0xFX0FETUlOIn0.f1XIipvaCNW-0qh_9zxzdiil5fAtHQhjA4ES8XwGe5LE-Wz85zRsLh3_eYAeIYdpROFgjk6vCZPN6NF7yaveOw",
            },
            success: function(data) {
                console.log("Success");

                // Clear any existing files in the dropdown
                var fileDropdown = $('#file-dropdown');
                fileDropdown.empty();
                fileDropdown.append($('<option></option>').val(null).html(null));

                for (var i = 0; i < data.length; i++) {
                    fileDropdown.append($('<option></option>').val(data[i].id).html(data[i].fileName))

                }
            },
            error: function() {
                console.log("Error");
            }
        });
    });

});