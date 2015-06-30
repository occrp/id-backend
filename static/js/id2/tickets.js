var ID2 = ID2 || {};
ID2.Tickets = {};

ID2.Tickets.init = function() {
    $("#filter_form").on("submit", ID2.Tickets.filterCurrent);
};

ID2.Tickets.filterCurrent = function() {
	// TODO: Ajaxize
	var filter = $("#filter_tickets").val();
	window.location.href = $.param.querystring(window.location.href, 'filter=' + filter);
}

$(function() {
	ID2.tickets.init();
});
