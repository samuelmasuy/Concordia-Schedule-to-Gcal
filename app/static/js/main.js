$(document).ready(function() {
  console.log("ready!");

  $('#spinner').hide();

  // on form submission ...
  $('form').on('submit', function() {

    console.log("the form has beeen submitted");
    url = $('input[name="url"]').val();
    console.log(url);

    //for (var i = 15; i >= 0; i-=5) {
        $.ajax({
          //beforeSend: function() {
            //$('#spinner').show();
          //},
          type: "POST",
          url: "/",
          data : { 'url': url},
          //complete: function() {
            //$('#spinner').hide();
          //},
          success: function(results) {
              //console.log(results);
              console.log("done")
              //$('#warning').html(results['error']);
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
    //}
  });
});
