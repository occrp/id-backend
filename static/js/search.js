$(document).ready(function() {
  $('.more_from_provider').on('click', function () {
    var provider = $(this).data('searchprovider');
    $('#s2id_search_providers').select2("data", [{id: provider, text: provider}]);    
    $('form.search').submit();
    });
    
  var offset = parseInt($('input[name=offset]').attr('value'), 10);
  var limit = parseInt($('input[name=limit]').attr('value'), 10);

  // search navigation
  $('#results_next').on('click',function () {
    $('input[name=offset]').attr('value', offset + limit);			    
    $('form.search').submit();
			});

  $('#results_prev').on('click',function () {
    $('input[name=offset]').attr('value', offset - limit);			    
    $('form.search').submit();
			});


  if(offset <= 0){
    $('#results_prev').prop('disabled', true);
  }
  if(offset+limit >= result_count){
    $('#results_next').prop('disabled', true); 
  }

  //tag links should add tag to the current search
  $('.tag_link').click(function(){
        console.log($(this).data('tag'));
        $('input[name=offset]').attr('value', 0);
        $('input[name=query]').attr('value',
           $('input[name=query]').attr('value') + ' tags:"' + $(this).data('tag') + '"'
				   );
        $('form.search').submit()
	return false;
		       });

  // clicking everything should (un)select everything
  $('input#search_providers-0').change(function(){
   $('input[name=search_providers]').prop('checked', $(this).is(':checked'));

  });

  // clicking search button should reset pagination
  $('button#newsearch').click(function(){
    $('input[name=offset]').attr('value', 0);
    $('form.search').submit()
});
});
