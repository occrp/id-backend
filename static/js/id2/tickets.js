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

ID2.Tickets.assign_user = function(ticket, user, callback) {
    $.post('/ticket/' + ticket + '/join/', {'user': user}), function(data) {
        if (callback) {
            callback(data);
        }
    });
}

ID2.Tickets.unassign_user = function(ticket, user) {
    $.post('/ticket/' + ticket + '/leave/', {'user': user}), function(data) {
        if (callback) {
            callback(data);
        }
    });
}

$(function() {
	ID2.tickets.init();
});
