(function($) {
  $(document).ready(function() {
    // Show/hide forms when selecting research goals
    $("input[name='ticket_type-ticket_type']").change(function() {
      $('.request-submit').show();
      $('.ticket-form').hide();
      $('#' + $(this).val() + '_form').show();
    });

    // Show correct form on load
    var ticket_type = $('input[name=ticket_type-ticket_type]:checked').val();
    if (ticket_type) {
      $('#' + ticket_type + '_form').show();
      $('.request-submit').show();
    }
  });
})(window.jQuery);
