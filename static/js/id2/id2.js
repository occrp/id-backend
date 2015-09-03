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


ID2.App = angular.module('ID2', ['ngMaterial']);

ID2.App.config(function($mdThemingProvider) {
  var ID2DarkPalette = $mdThemingProvider.extendPalette('blue-grey', {
      '500': '#3A4953',
  });
  var ID2LightPalette = $mdThemingProvider.extendPalette('blue-grey', {});
  $mdThemingProvider.definePalette('ID2Dark', ID2DarkPalette);
  $mdThemingProvider.definePalette('ID2Light', ID2LightPalette);
  $mdThemingProvider.theme('default').primaryPalette('ID2Dark');
  $mdThemingProvider.theme('dark').primaryPalette('ID2Dark');
  $mdThemingProvider.theme('dark').dark();
});

ID2.App.run(function($http) {
  $http.defaults.xsrfHeaderName = 'X-CSRFToken';
  $http.defaults.xsrfCookieName = 'csrftoken';
});
