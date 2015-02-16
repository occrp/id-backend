// var exports = window;

(function($) {
  // Handle all things date/time related
  var DateTime = {};

  DateTime.init = function() {
    DateTime.rewriteInputs();
    DateTime.rewriteSpans();
  };

  DateTime.rewriteInputs = function() {
    // Rewrite all inputs with moment before instantiating Bootstrap datepicker
    $('.datepicker').each(function() {
      var $el = $(this);
      var date = $el.data('date');
      if (date) {
        $el.val(moment(date).format('l'));
      }
      $el.datepicker({format: 'd/m/yyyy'}); // TODO: Figure out how to get datepicker to use Moment.js
    });
  };

  DateTime.rewriteSpans = function() {
    // Rewrite all dates wrapped in date spans
    $('span.date').each(function() {
      var $el = $(this);
      var datetime = $el.data('date');
      var format = $el.data('format');
      $el.text(moment(datetime).format(format));
    });

    // Rewrite all date/times wrapped in datetime spans
    $('span.datetime').each(function() {
      var $el = $(this);
      var datetime = $el.data('datetime');
      var format = $el.data('format');

      // Display datetimes in local time
      $el.text(moment.utc(datetime).local().format(format));
    });
  };

  window.DateTime = DateTime;

})(window.jQuery);
