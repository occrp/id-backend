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
}

$(ID2.init);

//
// ID2.App = angular.module('ID2', ['ngMaterial']);
//
// ID2.App.config(function($mdThemingProvider) {
//   var ID2DarkPalette = $mdThemingProvider.extendPalette('blue-grey', {
//       '500': '#3A4953',
//   });
//   var ID2LightPalette = $mdThemingProvider.extendPalette('blue-grey', {});
//   $mdThemingProvider.definePalette('ID2Dark', ID2DarkPalette);
//   $mdThemingProvider.definePalette('ID2Light', ID2LightPalette);
//   $mdThemingProvider.theme('default').primaryPalette('ID2Dark');
//   $mdThemingProvider.theme('dark').primaryPalette('ID2Dark');
//   $mdThemingProvider.theme('dark').dark();
// });
//
// ID2.App.run(function($http) {
//   $http.defaults.xsrfHeaderName = 'X-CSRFToken';
//   $http.defaults.xsrfCookieName = 'csrftoken';
// });
