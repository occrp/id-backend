ID2.Projects.controller('ID2.Projects.view', ['$scope', '$http', '$location', '$routeParams', '$mdDialog', function($scope, $http, $location, $routeParams, $mdDialog) {
    $scope.project = { users: []};
    $scope.storyList = [];

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
            if (!data) { return; }
            $http.post('/api/projects/' + $scope.project.id + '/stories/', data).
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
