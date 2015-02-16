// var exports = window;

(function($) {
  var ExternalDBs = {};

  ExternalDBs.init = function() {
    $('.ext-db-filter #id_country').on('change', function(e) {
      $('.ext-db-filter').submit();
      console.log("Submitted!");
    });
  };

  window.ExternalDBs = ExternalDBs;

})(window.jQuery);
