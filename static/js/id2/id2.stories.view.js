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
