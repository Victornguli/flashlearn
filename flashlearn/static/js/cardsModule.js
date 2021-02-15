var cardsModule = (function () {
    "use strict";

    function bindEvents() {
        // Edit Card Form Handler
        $("#edit-card-form").submit(function (e) {
            e.preventDefault();
            const cardId = $(this).find("#edit-card-id").val();
            $.ajax({
                url: `card/${cardId}/edit`,
                method: "POST",
                data: {
                    front: $(this).find("#edit-card-front").val(),
                    back: $(this).find("#edit-card-back").val(),
                },
                async: false,
                success: function (res) {
                    Toast.fire({
                        icon: "success",
                        title: `Success: Card updated successfully`,
                    });
                    $("#edit-card-modal").modal("hide");
                    setTimeout(() => {
                        window.location.reload();
                    }, 500);
                },
                error: function (err) {
                    e.preventDefault();
                    Toast.fire({
                        icon: "error",
                        title: `Error: Failed to update card`,
                    });
                },
            });
        });

        // Add Card Form Handler
        $("#add-card-form").submit(function (e) {
            e.preventDefault();
            console.log(this);
        });

        // Delete Card click handler
        // $(".delete-card").click(function () {
        //     const cardId = $(this).attr("card-id");
        //     Swal.fire({
        //         title: "Confirm Card deletion!",
        //         text: "This card will be deleted permanently.",
        //         icon: "warning",
        //         showCancelButton: true,
        //         cancelButtonColor: "#3085d6",
        //         confirmButtonColor: "#d33",
        //         confirmButtonText: "Delete it",
        //     }).then(function (result) {
        //         if (result.value) {
        //             $.ajax({
        //                 method: "POST",
        //                 url: `/card/${cardId}/delete`,
        //                 success: function (res) {
        //                     Swal.fire({
        //                         text: "Success: Card deleted succesfully",
        //                         icon: "success",
        //                     }).then(() => {
        //                         location.reload();
        //                     });
        //                 },
        //                 error: function (err) {
        //                     Toast.fire({
        //                         icon: "error",
        //                         title:
        //                             "Error: Failed to delete card. Try again later",
        //                     });
        //                 },
        //             });
        //         }
        //     });
        // });

        // Handle Edit Modal open
        $("#edit-card-modal").on("show.bs.modal", function (e) {
            const cardId = $(e.relatedTarget).attr("card-id");
            $.ajax({
                url: `card/${cardId}`,
                method: "GET",
                data: {},
                async: false,
                success: function (res) {
                    $("#edit-card-form")
                        .find("#edit-card-front")
                        .val(res["front"]);
                    $("#edit-card-form")
                        .find("#edit-card-back")
                        .val(res["back"]);
                    $("#edit-card-form").find("#edit-card-id").val(res["id"]);
                    $("#edit-card-modal").modal("show");
                },
                error: function (err) {
                    e.preventDefault();
                    Toast.fire({
                        icon: "error",
                        title: `Failed to retrieve card. Try again later`,
                    });
                },
            });
        });
    }
    
    function init() {
        bindEvents();
    }

    return {
        init: init,
    };
})();
