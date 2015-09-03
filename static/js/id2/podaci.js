ID2.App.controller('ID2PodaciCtrl', ['$scope', '$http', '$location',
  function($scope, $http, $location) {

  $scope.query = '';
  $scope.files = {};
  $scope.collections = {};

  var updateFiles = function() {
    $http.get('/podaci/file/', {params: {q: $scope.query}}).then(function(res) {
      $scope.files = res.data;
      console.log(res.data);
    });
  };

  var updateCollections = function() {
    $http.get('/podaci/collection/').then(function(res) {
      $scope.collections = res.data;
      console.log(res.data);
    });
  };

  updateFiles();
  updateCollections();
}]);
