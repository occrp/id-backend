// var exports = window;

(function($) {
  var ValidationForm = {};

  ValidationForm._validate = function(e) {
    var $this = $(e.target),
        $form = $this.closest("form"),
        data_url = $form.data('validation-url'),
        validation_marker = $form.find('.validation-marker');

    if (validation_marker.length == 0) {
      // ensure that the validation marker is present in the form.
      validation_marker = $("<div class='validation-marker'/>");
      $form.find('button[type="submit"]').parent().append(validation_marker);
    }

    // ping the server with the form values (only input, select)
    $.ajax({
      url: data_url,
      type: 'POST',
      data: $form.find("input, select, textarea").serialize(),
      success: function(data) {
        if (data.status) {

          validation_marker.empty();
          // create an icon with a tooltip of the returned message.
          var icon = $("<i data-toggle='tooltip' title='"+data.message+"'/>");

          if (data.status != "valid") {
            icon.addClass('icon-warning-sign');
          } else {
            icon.addClass('icon-ok-sign');
          }

          icon.tooltip();
          validation_marker.append(icon);
        }
      },
      error: function(x) {
        // Let the user know that something went wrong. 
        Alert.show(i18n.gettext('There was a problem with validation.'));
      }
    });
  };

  ValidationForm.validate = _.debounce(ValidationForm._validate, 500); 

  $(document).ready(function() {
    $(document).on('keyup change', '[data-validation-url] input, [data-validation-url] textarea', ValidationForm.validate);
  });

  window.ValidationForm = ValidationForm;

})(window.jQuery);
