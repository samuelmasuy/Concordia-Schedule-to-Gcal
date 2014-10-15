$(document).ready(function() {
  console.log("ready!");
  $('grab_url').show()
  $('#spinner').hide();
  $('#thank_you').hide();
  $('#result').hide();

    var opts = {
      lines: 13, // The number of lines to draw
      length: 20, // The length of each line
      width: 10, // The line thickness
      radius: 30, // The radius of the inner circle
      corners: 1, // Corner roundness (0..1)
      rotate: 0, // The rotation offset
      direction: 1, // 1: clockwise, -1: counterclockwise
      color: '#000', // #rgb or #rrggbb or array of colors
      speed: 1, // Rounds per second
      trail: 60, // Afterglow percentage
      shadow: false, // Whether to render a shadow
      hwaccel: false, // Whether to use hardware acceleration
      className: 'spinner', // The CSS class to assign to the spinner
      zIndex: 2e9, // The z-index (defaults to 2000000000)
      top: '50%', // Top position relative to parent
      left: '50%' // Left position relative to parent
    };
    var target = document.getElementById('spinner');
    var spinner = new Spinner(opts).spin(target);

  // on form submission ...
  $('form').on('submit', function() {

    var url = $('input[name="url"]').val();
    console.log(url);

    $.ajax({
      beforeSend: function() {
        $('#spinner').show();
      },
      type: "POST",
      url: "/",
      data : { 'url': url},
      complete: function() {
        spinner.stop();
        $('#spinner').hide();
      },
      success: function(results) {
          //console.log(results);
          console.log("done")
          $('#grab_url').hide();
          $('#result').show();
          $('#thank_you').show();
      },
      statusCode: {
        400: function(error) {
          $('#warning').html(error.responseJSON.message);
        },
        500: function(error) {
            console.log(error)
        }
       }
    });
  });
});
