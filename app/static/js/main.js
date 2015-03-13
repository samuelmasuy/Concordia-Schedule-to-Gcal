$(document).ready(function() {
    $('grab_url').show();
    $('#spinner').hide();
    $('#thank_you').hide();
    $('#result').hide();
    var opts = {
        lines: 14, // The number of lines to draw
        length: 22, // The length of each line
        width: 9, // The line thickness
        radius: 35, // The radius of the inner circle
        corners: 0.5, // Corner roundness (0..1)
        rotate: 0, // The rotation offset
        direction: 1, // 1: clockwise, -1: counterclockwise
        color: '#2c3e50', // #rgb or #rrggbb or array of colors
        speed: 1.2, // Rounds per second
        trail: 68, // Afterglow percentage
        shadow: true, // Whether to render a shadow
        hwaccel: false, // Whether to use hardware acceleration
        className: 'spinner', // The CSS class to assign to the spinner
        zIndex: 2e9, // The z-index (defaults to 2000000000)
        top: '50%', // Top position relative to parent
        left: '50%' // Left position relative to parent
    };
    var target = document.getElementById('spinner');
    var spinner = new Spinner(opts).spin(target);
    $('.form-horizontal').bootstrapValidator({
        fields: {
            username: {
                validators: {
                    notEmpty: {
                        message: 'The username is required and cannot be empty'
                    },
                    stringLength: {
                        min: 4,
                        max: 9,
                        message: 'The username must be more than 4 and less than 9 characters long'
                    },
                    regexp: {
                        regexp: /^[A-z]+_[A-z]+$/,
                        message: 'The username can only consist of alphabetical character and must contain an underscore'
                    },
                    invalidCredit: {
                        message: ''
                    }
                }
            },
            password: {
                validators: {
                    notEmpty: {
                        message: 'The password is required and cannot be empty'
                    },
                    regexp: {
                        regexp: /^.*$/,
                        message: 'The password format is not correct'
                    },
                    stringLength: {
                        min: 3,
                        max: 25,
                        message: 'The password must be more than 3 and less than 25 characters long'
                    },
                    invalidCredit: {
                        message: ''
                    }
                }
            }
        }
    }).on('success.form.bv', function(e) {
        // Prevent form submission
        e.preventDefault();

        // Get the form instance
        var $form = $(e.target);

        // Get the BootstrapValidator instance
        var bv = $form.data('bootstrapValidator');

        var csrftoken = $('meta[name=csrf-token]').attr('content');

        // Use Ajax to submit form data
        $.ajax({
            type: "POST",
            url: $form.attr('action'),
            data: $form.serialize(),
            beforeSend: function(xhr, settings) {
                if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
                $('#spinner').show();
            },
            complete: function() {
                spinner.stop();
                $('#spinner').hide();
            },
            success: function(results) {
                $('#grab_url').hide();
                $('#result').show();
                $('#thank_you').show();
                $('#save').click(function() {
                    var file = 'Concordia Class Schedule.ics';
                    var blob;
                    if (navigator.userAgent.indexOf('MSIE 10') === -1) { // chrome or firefox
                        blob = new Blob([results['ical']]);
                    } else { // ie
                        var bb = new BlobBuilder();
                        bb.append(results['ical']);
                        blob = bb.getBlob('text/x-vCalendar;charset=' + document.characterSet);
                    }
                    saveAs(blob, file);
                });
                $('#save').show();
            },
            statusCode: {
                400: function(error) {
                    error_messages = error.responseJSON.message;
                    var field_error;
                    var validator_field_error;
                    for (var key in error_messages) {
                        field_error = key;
                        var obj = error_messages[key];
                        for (var prop in obj) {
                            validator_field_error = obj[prop];
                            bv.updateStatus(field_error, 'INVALID', validator_field_error);
                        }
                    }
                },
                401: function(error) {
                    error_messages = error.responseJSON.message;
                    bv.updateStatus('username', 'INVALID', 'invalidCredit');
                    bv.updateStatus('password', 'INVALID', 'invalidCredit');
                    $('#warning').html(error_messages);
                    $('#password').val("");
                },
                500: function(error) {
                    var w = window.open('', 'debug_stuff', 'width=540,height=150');
                    w.document.open();
                    w.document.write(error.responseText);
                    w.document.close();
                }
            }
        });
    });
    $('input#password').focus(function() {
        $("#warning").empty();
        $('.form-horizontal').data('bootstrapValidator').revalidateField('username');
    });
});
