// var exports = window;


(function($) {
  /**
   * A Simple mechanism to accomplish modal forms via template fragments
   * implemented on the server rather than any complex JS to do form
   * validation, etc.
   */
  var FormRegistry = {};

  var can_serialize = function(form){
  // we can serialize a form if it doesn't have any file uploads
  return form.find('input[type=file]').length === 0; 
  }



  /**
   * Captures form submissions and sends
   */
  FormRegistry.handleSubmit = function($modal, keepEvents) {
    var $body = $('.modal-body', $modal);
    var $content = $('.modal-content', $modal);
    var $submit = $('.submit', $modal);
    var spinner = new IDSpinner({before: $submit});

    // Register submit handler
    $submit.on('click', function() {
      var $form = $('form', $modal);
      if(can_serialize($form)){
      var action = $form.attr('action');
      spinner.spin();
      $.ajax({
        url: action,
        type: 'POST',
        data: $form.serialize(),
        success: function(data) {
          if (data.status == 'error') {
            // Replace modal body with error HTML and ensure the form
            // action doesn't get lost
            $content.html(data.html);
            $('form', $content).attr('action', action);

            App.initWidgets();
            var err = $('.error', $modal);
            if (err.length > 0) {
              $body.scrollTo(err);
            }
          } else {
            if (data.data) {
              var search = window.location.search;
              if (search.length > 0) {
                if (search.search("data=") > -1 ) {
                  // replace the data url param
                  search = search.substr(0, search.search("data=")) + "data=" + data.data;
                } else {
                  // append the data url param
                  search += "&data=" + data.data;
                }
              } else {
                // append the blank url param
                search = "?data=" + data.data;
              }
              if (window.location.search == search) {
                window.location.reload()
              } else {
                window.location.search = search;
              }

            } else {
              window.location.reload();
            }
          }
        },
        error: function() {
          Alert.show('There was an error submitting this form. Please try ' +
            'again.', 'error', $('.modal-alerts', $modal), $body);
        },
        complete: function () {
          spinner.stop();
        }
      });
      return false;
}

else {
    $form.submit();
}
    });

    if (!keepEvents) {
      // Unregister submit handler when modal closes
      $modal.on('hidden.bs.modal', function() {
        $submit.off('click');
        $modal.off('hidden.bs.modal');
      });
    }
  };

  /**
   * Provide the ID of the modal you wish to hook up.
   */
  FormRegistry.register = function(modalID) {
    FormRegistry.handleSubmit($('#' + modalID), true);
  };

  /**
   * Shows a modal with a dynamically fetched body.
   */
  FormRegistry.showDynamicModal = function(modalID, modalUrl) {
    var $modal = $(modalID).modal();
    var $content = $('.modal-content', $modal);
    $content.empty();
    var spinnerTarget = $("<span/>");
    $content.append(spinnerTarget);
    var spinner = new IDSpinner({target: spinnerTarget});
    spinner.spin();
    $.ajax({
      url: modalUrl,
      type: 'GET',
      success: function(data) {
        $content.html(data.html);
        App.initWidgets();
        FormRegistry.handleSubmit($modal, false);
      },
      error: function() {
        Alert.show('There was an error loading this dialog. Please try again.',
          'error', $('.modal-alerts', $modal), $('.modal-body', $modal));
      },
      complete: function () {
        spinner.stop();
      }
    });
  };

  $(document).ready(function() {
    $('[data-modal-url]').on('click', function() {
      var $this = $(this);
      FormRegistry.showDynamicModal($this.attr('href'),
        $this.data('modal-url'));
    });
  });

  window.FormRegistry = FormRegistry;

})(window.jQuery);
