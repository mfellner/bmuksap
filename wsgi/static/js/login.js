/**
 * Copyright 2013 Maximilian Fellner
 */

$(document).ready(function () {
    $("#login-form").parsley();

    $("#btn-login").mousedown(function () {
        if ($('#login-form').parsley('isValid')) {
            setOnSubmitListener();
        }
    });
});

function setOnSubmitListener() {
    $("#login-form").submit(function (e) {
        console.log("button click");
        var self = this;
        e.preventDefault();
        $("#login-form").fadeOut(400, function () {
            var opts = {
                length: 20,
                width: 10,
                radius: 30,
                hwaccel: true,
                top: '100em'
            };
            var target = document.getElementById("page-content");
            new Spinner(opts).spin(target);
            self.submit();
            return false;
        });
    });
}
