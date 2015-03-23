$(function() {
	register_anchor_forms();
});

/* allows links to function as simple submit buttons to
post custom actions to the server */
function register_anchor_forms() {
	$('a.anchor_form').click(function(e) {
		e.preventDefault();
		console.log("a click!");
		$form = $('<form action="'+$(this).data('action')+'" method="POST" class="inline-form">\
					<input type="hidden" name="csrfmiddlewaretoken" value="'+$(this).data('csrf')+'">\
				 </form>');
		$('body').append($form);
		$form.submit();
		console.log($form);
	});
}