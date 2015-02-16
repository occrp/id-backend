$(document).ready(function() {

 var load_entity_view = function() {
    var $this = $(this);
    var $modal = $('#entity-viewer');
    $.ajax({
      url: $this.data('url'),
      data: {
        key: $this.data('key'), 
        query: $this.data('query')
      },
      success: function (data) {
        $modal.html(data);
        $modal.modal('show');
        App.initWidgets();
        $('.entity-view').on('click', load_entity_view) 
      }
    });
  };
  $('.entity-view').on('click', load_entity_view) 
  $('#info-box-open').on('click', function(){
   $('#info-box-viewer').modal('show');
   });
  $('#info-box-close').on('click', function(){
    $('#info-box-viewer').modal('hide');
  });
 

});

