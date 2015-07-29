var ID2 = ID2 || {};

ID2.ng = angular.module('ID2', ['ngRoute', 'ngMaterial', 'ID2.Projects']).
    config(['$routeProvider', function($routeProvider) {
        $routeProvider.otherwise({redirectTo: '/projects'});
    }]).
    config(function($mdThemingProvider) {
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


function DialogController($scope, $mdDialog) {
    $scope.cancel = function() {
        $mdDialog.cancel();
    };
    $scope.create = function(data) {
        $mdDialog.hide(data);
    };
}


/*
{
    "title": "The Missing Millions",
    "thesis": "Millions of dollars that went missing after a truck took a wrong turn and got ambushed by radioactive vampires.",
    "versions": "43",
    "authors": [
        {"name": "Dave Bloss", "email": "dave@occrp.org"},
        {"name": "Miranda Patrucic", "email": "miranda@occrp.org"},
    ],
},
{
    "title": "Rustlers on the Moor",
    "thesis": "A bunch of horses went missing, but later turned up in a meatball stew served at a glue factory.",
    "versions": "2",
    "authors": [
        {"name": "Jody McPhillips", "email": "dave@occrp.org"},
        {"name": "Paul Radu", "email": "miranda@occrp.org"},
        {"name": "Lejla Camdzic", "email": "miranda@occrp.org"},
        {"name": "Matt Sarnecki", "email": "miranda@occrp.org"},
    ],
},
{
    "title": "Deep-one Trafficking at All Time High",
    "thesis": "Cthulu's spawn are being traded on open markets in the East, creating demand which is being satisfied by cross-border smuggling of these aquatic demigods.",
    "versions": "2",
    "authors": [
        {"name": "Paul Radu", "email": "miranda@occrp.org"},
        {"name": "Smári McCarthy", "email": "miranda@occrp.org"},
        {"name": "Eleanor Rose", "email": "miranda@occrp.org"},
    ],
}

*/
