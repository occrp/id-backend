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
