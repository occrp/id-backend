var ID2 = ID2 || {};
ID2.Tickets = {};

/* current_user_id is assigned in base.jina */

ID2.Tickets.init = function() {
    $("#filter_form").on("submit", ID2.Tickets.filterCurrent);
    ID2.Tickets.buttonHandlers();
};

ID2.Tickets.buttonHandlers = function() {
    $(".leave_btn").off("click");
    $(".leave_btn").on("click", function(event) {
        event.preventDefault();
        ID2.Tickets.leave_user($(this).data('key'), $(this).data('user'), $(this).data('display-name'), $(this));
    });

    $(".add_assignee_btn").off("click");
    $(".add_assignee_btn").on("click", function(event) {
        select = $(this).parent().find('select')
        event.preventDefault();

        if($(select).find('option:selected').val() == 0) {
            return;
        }

        ID2.Tickets.assign_user($(select).data('key'), $(select).find('option:selected').val(), $(select).find('option:selected').text(), $(select));
    });

    $(".join_btn").off("click");
    $(".join_btn").on("click", function(event) {
        event.preventDefault();
        ID2.Tickets.join_user($(this).data('key'), $(this).data('user'), $(this).data('display-name'), $(this));
    });

    $(".remove_user").off("click");
    $(".remove_user").on("click", function(event) {
        event.preventDefault();
        ID2.Tickets.unassign_user($(this).data('key'), $(this).data('user'), $(this).parent());
    });
}

ID2.Tickets.filterCurrent = function() {
	// TODO: Ajaxize
	var filter = $("#filter_tickets").val();
	window.location.href = $.param.querystring(window.location.href, 'filter=' + filter);
}

ID2.Tickets.createAssigneeSpan = function(ticket, user, display_name) {
    return '<span class="assignee" style="background: #eee; padding: 2px; border: 1px solid #ccc;"> \
        <a href="/accounts/profile/'+user+'">'+display_name+'</a> \
        <a class="remove_user" href="#" data-key="'+ticket+'" data-user="'+user+'"><i class="fa fa-close"></i></a> \
    </span>';
}

ID2.Tickets.updateAssigneeSelect = function(working_element, user, visible) {
    found_visible = false;
    working_element.find('option').each(function(e) {
        if($(this).val() == user) {
            if(visible) {
                $(this).show();
            } else {
                $(this).hide();
            }
        }

        if($(this).val() == 0) {
            $(this).attr("selected", "selected")
        } else {
            $(this).removeAttr("selected");
        }
    });

}

// ID2.Tickets.assign_user = function(ticket, user, callback) {
//     $.post('/ticket/' + ticket + '/join/', {'user': user}, function(data) {
//         if (callback) {
//             callback(data);
//         }
//     });
// }

ID2.Tickets.assign_user = function(ticket, user, display_name, working_element) {
    $.ajax({
        url: '/ticket/' + ticket + '/assign/',
        type: 'POST',
        data: {'user': user},
        success: function(data) {
            ID2.Tickets.updateAssigneeSelect(working_element, user, false);

            if(user == current_user_id) {
                leave_button = working_element.parent().parent().parent().find('.leave_btn');
                leave_button.css('display', '');
                join_button = leave_button.parent().find('.join_btn');
                join_button.css('display', 'none');
            }

            working_element.parent().parent().parent().parent().find('span').first().after(
                ID2.Tickets.createAssigneeSpan(ticket, user, display_name)
            );
            ID2.Tickets.buttonHandlers();
        },
        error: function(data) {
            Alert.show(data.responseJSON.message, 'error', $('#alerts'), $('body'));
        }
    });
}

ID2.Tickets.unassign_user = function(ticket, user, removable_element) {
    $.ajax({
        url: '/ticket/' + ticket + '/unassign/',
        type: 'POST',
        data: {'user': user},
        success: function(data) {

            ID2.Tickets.updateAssigneeSelect(removable_element.parent().find('.pull-right').find('select'), user, true);

            if(user == current_user_id) {
                leave_button = removable_element.parent().find('.pull-right').find('.leave_btn');
                leave_button.css('display', 'none');
                join_button = leave_button.parent().find('.join_btn');
                join_button.css('display', '');
            }

            removable_element.remove();
        },
        error: function(data) {
            Alert.show(data.responseJSON.message, 'error', $('#alerts'), $('body'));
        }
    });
}

ID2.Tickets.join_user = function(ticket, user, display_name, working_element) {
    $.ajax({
        url: '/ticket/' + ticket + '/assign/',
        type: 'POST',
        data: {'user': user},
        success: function(data) {

            ID2.Tickets.updateAssigneeSelect(working_element.parent().find('select'), user, false);

            working_element.css('display', 'none');
            leave_button = working_element.parent().find('.leave_btn');
            leave_button.css('display', '');

            working_element.parent().parent().find('span').first().after(
                ID2.Tickets.createAssigneeSpan(ticket, user, display_name)
            );
            ID2.Tickets.buttonHandlers();
        },
        error: function(data) {
            Alert.show(data.responseJSON.message, 'error', $('#alerts'), $('body'));
        }
    });
}

ID2.Tickets.leave_user = function(ticket, user, display_name, working_element) {
    $.ajax({
        url: '/ticket/' + ticket + '/unassign/',
        type: 'POST',
        data: {'user': user},
        success: function(data) {

            ID2.Tickets.updateAssigneeSelect(working_element.parent().find('select'), user, true);

            working_element.css('display', 'none');
            join_button = working_element.parent().find('.join_btn');
            join_button.css('display', '');

            working_element.parent().parent().find('a').each(function(index) {
                if($(this).text() == display_name) {
                    $(this).parent().remove();
                }
            });
        },
        error: function(data) {
            Alert.show(data.responseJSON.message, 'error', $('#alerts'), $('body'));
        }
    });
}

$(function() {
	ID2.Tickets.init();
});

$.ajaxSetup({
     beforeSend: function(xhr, settings) {
         function getCookie(name) {
             var cookieValue = null;
             if (document.cookie && document.cookie != '') {
                 var cookies = document.cookie.split(';');
                 for (var i = 0; i < cookies.length; i++) {
                     var cookie = jQuery.trim(cookies[i]);
                     // Does this cookie string begin with the name we want?
                     if (cookie.substring(0, name.length + 1) == (name + '=')) {
                         cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                         break;
                     }
                 }
             }
             return cookieValue;
         }
         if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
             // Only send the token to relative URLs i.e. locally.
             xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
         }
     }
});
