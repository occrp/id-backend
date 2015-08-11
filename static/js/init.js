// var exports = window;

(function($) {
  var App = {};

  App.initWidgets = function() {
    DateTime.init();
    Select2Field.init();
    RelationshipTypeField.init();
    $('select:not(.not_select2)').select2({width: '220px'});
    ExternalDBs.init();
  };

  $(document).ready(function() {
    App.initWidgets();
  });

  window.App = App;

})(window.jQuery);
