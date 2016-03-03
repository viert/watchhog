var watchCtrl = angular.module('watchCtrl', []);

watchCtrl.run([ '$rootScope', '$sce', '$route', function($scope, $sce, $route) {
    $scope.formatArgs = function(args) {
        var result = [];
        for (var i in args) {
            result.push('<span class="text-danger">"' + args[i] + '"</span>');
        }
        return $sce.trustAsHtml( result.join(", ") );
    };

    $scope.activeMenuItem = function(section) {

        return $route.current && $route.current.section && $route.current.section == section;
    };

    $scope.global = {};
}]);

var OverviewController = watchCtrl.controller('OverviewController', [ '$scope', '$http', '$timeout', function($scope, $http, $timeout) {
    if ($scope.global.updater) $timeout.cancel($scope.global.updater);
    $scope.getData = function() {
        $http.get('/api/stats/threads')
            .then(function(data) {
                $scope.threads = data.data.threads;
            });
        $http.get('/api/stats/tasks')
            .then(function(data) {
                $scope.tasks = data.data.tasks;
                $scope.global.updater = $timeout($scope.getData, 1000);
            }, function() {
                $scope.global.updater = $timeout($scope.getData, 1000);
            });
    };
    $scope.getData();
}]);

var StoreListController = watchCtrl.controller('StoreListController', [ '$scope', '$http', '$timeout', function($scope, $http, $timeout) {
    if ($scope.global.updater) $timeout.cancel($scope.global.updater);
    $scope.tables = {};
    $scope.getData = function() {
        $http.get('/api/tables').then(function(data) {
            for (var i in data.data.tables) {
                var table = data.data.tables[i];
                $http.get(table.link).then(function(data) {
                    $scope.tables[table.name] = data.data.table;
                });
            }
        });
    };
    $scope.getData();
}]);

var watchRts = angular.module('watchRts', ['ngRoute']);

watchRts.config([ '$routeProvider', function($routeProvider) {
    $routeProvider
        .when('/overview', {
            controller: 'OverviewController',
            templateUrl: '/templates/overview.html',
            section: 'overview'
        })
        .when('/store', {
            controller: 'StoreListController',
            templateUrl: '/templates/store_list.html',
            section: 'store'
        })
        .otherwise({
            redirectTo: '/overview'
        });
}]);

var watchApp = angular.module('watchApp', ['watchCtrl', 'watchRts']);