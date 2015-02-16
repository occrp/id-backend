// var exports = window;

(function($) {
  var RelationshipTypeField = {};

  RelationshipTypeField.init = function() {
    if ($('.modal.in #relationship-left_type').length > 0) {
      RelationshipTypeField.initForNewEntities();
    } else {
      RelationshipTypeField.initForExistingEntities();
    }
  };

  RelationshipTypeField.initForNewEntities = function() {
    var leftType = $('.modal.in #relationship-left_type').val();
    var rightType = $('.modal.in #relationship-right_type').val();
    $.getJSON('/admin/relationship_types/', {
      left_type: leftType,
      right_type: rightType
    }, function(data) {
      $('.modal.in #relationship-type').select2({
        data: data
      });
    });
  };

  RelationshipTypeField.initForExistingEntities = function() {
    var leftType = $('input#left_type').val();
    var rightEl = $('input#right');
    if (leftType && rightEl.length > 0) {
      RelationshipTypeField.populateTypes(leftType, rightEl.val());
      rightEl.on('change', function() {
        RelationshipTypeField.populateTypes(leftType, rightEl.val());
      });
    }
  };

  RelationshipTypeField.populateTypes = function(leftType, rightKey) {
    var args = {
      left_type: leftType,
      right: rightKey
    };
    if (!rightKey) {
      args = { all_types: true };
    }
    $.getJSON('/admin/relationship_types/', args, function(data) {
      $('input#type').select2({data: data});
    });
  };

  window.RelationshipTypeField = RelationshipTypeField;

})(window.jQuery);
