var ID2 = ID2 || {};

ID2.init = function() {
    ID2.Notifications.init();
}

// Notifications subsystem
ID2.Notifications = {};
ID2.Notifications.init = function() {
    $("#notifications_allread").on("click", function(e) {
        e.stopPropagation();
        $.getJSON("/notifications/seen/all/", function(data) {
            $(".notification").removeClass("unseen");
            $("#notifications_count").text(data.unseen_count);
        });
    });
    $(".notification").on("click", function(e) {
        var it = e.target;
        e.stopPropagation();
        $.getJSON("/notifications/seen/" + $(it).data("id") + "/", function(data) {
            $(it).removeClass("unseen");
            $("#notifications_count").text(data.unseen_count);
        });
    });

    if ($(".notification_stream").length) {
        ID2.Notifications.streamer_init();
    }
}

ID2.Notifications.streamer_init = function() {
    ID2.Notifications.poll();
    ID2.Notifications.streamer_timer = setInterval(ID2.Notifications.poll, 5000);
}

ID2.Notifications.poll = function() {
    console.log("polling");
    $.getJSON("/notifications/stream/", function(data) {
        for (i in data) {
            noti = data[i];
            
        }
        $(".notification_stream").html("<pre>" + JSON.stringify(data) + "</pre>");
    });
}

$(ID2.init);
