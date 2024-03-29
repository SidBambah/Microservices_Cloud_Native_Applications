//var app = angular.module("CustomerApp", []);

CustomerApp.controller("profileController", function($scope, $http, $location, $window) {

    console.log("Profile controller loaded.")

    var s3 = jQuery.LiveAddress({
        key: "369686634285375",
        waitForStreet: true,
        debug: true,
        target: "US",
        placeholder: "Enter address",
        addresses: [{
            freeform: '#newaddress'
        }]
    });

    s3.on("AddressAccepted", function(event, data, previousHandler)
    {
        console.log("Boo Yah!")
        console.log(JSON.stringify(data.response, null,3))

    });

    $scope.placeholder = "enter an address and select a choice."

    $scope.addressKinds = ['Home', 'Work', 'Other']

    $scope.addressKind = function(idx) {
        console.log("Address kknk = " + $scope.addressKinds[idx]);
    };

});

