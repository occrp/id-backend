var ID2 = ID2 || {};

ID2.ng = angular.module('ID2', ['ngRoute', 'ID2.Projects']).
    config(['$routeProvider', function($routeProvider) {
        $routeProvider.otherwise({redirectTo: '/projects'});
    }]);


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

function DialogController($scope, $mdDialog) {
    $scope.cancel = function() {
        $mdDialog.cancel();
    };
    $scope.create = function(data) {
        $mdDialog.hide(data);
    };
}


ID2.Projects.controller('ID2.Stories.view', ['$scope', '$http', '$location', '$routeParams', '$mdDialog', function($scope, $http, $location, $routeParams, $mdDialog) {
    $scope.story = {};
    $scope.storyVersion = {"text": ""};
    $scope.saveStatus = 100;

    $scope.textChanged = function() {
        $scope.saveStatus = 0;
    }

    $scope.save = function() {
        $scope.saveStatus = 0;
        $http.put('/api/stories/' + $scope.story.id + "/", $scope.storyVersion).
            success(function(data, status, headers, config) {
                $scope.saveStatus = 100;
            }).
            error(function(data, status, headers, config) {

            });
    }

    $scope.getStory = function(id) {
        $http.get('/api/stories/' + id + "/").
            success(function(data, status, headers, config) {
                $scope.story = data;
            }).
            error(function(data, status, headers, config) {
                // log error
            });
    }

    $scope.getStory($routeParams.storyId);
}]);


ID2.Projects.controller('ID2.Projects.view', ['$scope', '$http', '$location', '$routeParams', '$mdDialog', function($scope, $http, $location, $routeParams, $mdDialog) {
    $scope.project = { users: []};
    $scope.storyList = [
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
    ];

    $scope.openStory = function(item) {
        $location.path("/stories/" + item.id);
    }

    $scope.getProject = function(id) {
        $http.get('/api/projects/' + id + "/").
            success(function(data, status, headers, config) {
                $scope.project = data;
            }).
            error(function(data, status, headers, config) {
                // log error
            });
    }

    $scope.newStory = function(ev) {
        $mdDialog.show({
            controller: DialogController,
            templateUrl: '/static/html/id2/story.new.html',
            parent: angular.element(document.body),
            targetEvent: ev,
        })
        .then(function(data) {
            console.log(data);
            if (!data) { return; }
            data["project"] = $scope.project.id;
            console.log(data);
            $http.post('/api/stories/', data).
                success(function(data, status, headers, config) {
                    console.log("Success:" + data);
                    $scope.storyListUpdate();
                    $scope.openStory(data.story.id);
                }).
                error(function(data, status, headers, config) {
                    console.log("Error:" + data);
                });
            $scope.alert = data;
        }, function() {
            $scope.alert = 'You cancelled the dialog.';
        });
    };

    $scope.storyListUpdate = function() {
        $http.get('/api/projects/').
            success(function(data, status, headers, config) {
                $scope.storyList = data;
            }).
            error(function(data, status, headers, config) {
                // log error
            });
    }

    $scope.getUsers = function(query) {
        var retval = {};
        $http.get('/api/users/', {"q": query}).
            success(function(data, status, headers, config) {
                retval = data;
            }).
            error(function(data, status, headers, config) {

            });
        return retval;
    }

    $scope.getProject($routeParams.projectId);
}]);

ID2.Projects.controller('ID2.Projects.list', ['$scope', '$http', '$location', '$mdDialog', function($scope, $http, $location, $mdDialog) {
    $scope.setLocation = function(view) {
        $location.path(view);
    }

    $scope.selectProject = function(item) {
        $location.path("/projects/" + item.id);
    }

    $scope.newProject = function(ev) {
        $mdDialog.show({
            controller: DialogController,
            templateUrl: '/static/html/id2/project.new.html',
            parent: angular.element(document.body),
            targetEvent: ev,
        })
        .then(function(data) {
            if (!data) { return; }
            console.log(data);
            $http.post('/api/projects/', data).
                success(function(data, status, headers, config) {
                    console.log("Success:" + data);
                    $scope.projectListUpdate();
                }).
                error(function(data, status, headers, config) {
                    console.log("Error:" + data);
                });
            $scope.alert = data;
        }, function() {
            $scope.alert = 'You cancelled the dialog.';
        });
    };

    $scope.projectListUpdate = function() {
        $http.get('/api/projects/').
            success(function(data, status, headers, config) {
                $scope.projectList = data;
            }).
            error(function(data, status, headers, config) {
                // log error
            });
    }

    $http.defaults.xsrfHeaderName = 'X-CSRFToken';
    $http.defaults.xsrfCookieName = 'csrftoken';
    $scope.projectList = []
    $scope.projectListUpdate();
}]);
