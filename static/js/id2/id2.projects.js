
ID2.Projects = angular.module('ID2.Projects', ['ngMaterial']).
    config(['$routeProvider', function($routeProvider) {
        $routeProvider.
            when('/projects', {
                templateUrl: '/static/html/id2/project.list.html',
                controller: 'ID2.Projects.list'
            }).
            when('/projects/:projectId', {
                templateUrl: '/static/html/id2/project.view.html',
                controller: 'ID2.Projects.view'
            }).
            when('/stories/:storyId', {
                templateUrl: '/static/html/id2/story.view.html',
                controller: 'ID2.Stories.view'
            });
    }]);
