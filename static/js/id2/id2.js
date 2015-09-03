var ID2 = ID2 || {};

ID2.init = function() {
    ID2.Notifications.init();
}

// Notifications subsystem
ID2.Notifications = {};
ID2.Notifications.init = function() {
    $(".notification").on("click", function(e, it) {
        $.post("/notifications/seen/", {"id": $(it).data("id")}, function(data) {
            
        });
    })
}

$(ID2.init);
