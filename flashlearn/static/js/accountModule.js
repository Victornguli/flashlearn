var accountModule = (function () {
    "use strict";

    /**
     * Bind All account module events
     */
    function bindEvents() {
        // Change Password form handler
        $("#change-password-form").submit(function (e) {
            var loader = $("#change-password__submit-loader");
            var text = $("#change-password__submit-text");
            var button = $("#change-password__submit-button");
            formLoader(loader, text, button, "start");
            e.preventDefault();
            $.ajax({
                url: `/user/account/change_password`,
                method: "POST",
                data: {
                    old_password: $(this).find("#old_password").val(),
                    password: $(this).find("#password").val(),
                    confirm_password: $(this).find("#confirm_password").val(),
                },
                success: function (res) {
                    if (res["status"]) {
                        Toast.fire({
                            icon: "success",
                            title: `Success: Password updated successfully`,
                            timer: 5000,
                            timerProgressBar: false,
                        });
                        $("#change-password-form")[0].reset();
                        formLoader(loader, text, button, "stop");
                    } else {
                        Toast.fire({
                            icon: "error",
                            title: res["message"],
                            timer: 5000,
                            timerProgressBar: false,
                        });
                        formLoader(loader, text, button, "stop");
                    }
                },
                error: function (err) {
                    e.preventDefault();
                    Toast.fire({
                        icon: "error",
                        title: `Error: Failed to update password`,
                        timer: 5000,
                        timerProgressBar: false,
                    });
                    formLoader(loader, text, button, "stop");
                },
            });
        });

        // Listen to toggle password visibility
        $(".toggle-password").click(function () {
            const password = $(this).attr("passwordElement");
            const type =
                $(`#${password}`).attr("type") === "password"
                    ? "text"
                    : "password";
            $(`#${password}`).attr("type", type);
            $(this).toggleClass("fa-eye-slash");
        });
    }

    /**
     * Helper method for handing start and stop loading of submit button on account page forms
     * @param {HTMLElement} loader The loader/spinner to show progress
     * @param {HTMLElement} text The element containing the button text
     * @param {HTMLElement} button The submit button element
     * @param {string} step The current step in form handling(i.e start or stop)
     */
    function formLoader(loader, text, button, step) {
        if (step === "start") {
            $(loader).removeClass("d-none");
            $(text).addClass("d-none");
            $(button).prop("disabled", true);
        } else if (step === "stop") {
            $(loader).addClass("d-none");
            $(text).removeClass("d-none");
            $(button).prop("disabled", false);
        }
    }

    /**
     * Exposes accountModule
     */
    function init() {
        bindEvents();
    }

    return {
        init: init,
    };
})();
