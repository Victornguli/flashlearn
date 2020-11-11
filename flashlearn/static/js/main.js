$(document).ready(function () {
    // Init Select2 Options
    $(".select2").select2({
        placeholder: "Select an option",
        allowClear: true,
    });

    $(".select2_deck_cards").select2({
        placeholder: "Filter by state",
        allowClear: true,
    });

    $("#deck_name").select2({
        placeholder: "Filter by deck status",
        allowClear: true,
    });

    $('[data-toggle="tooltip"]').tooltip();

    // Toggle modal manually: When edit button also suports a tooltip
    // it is not possible to add data-target as the modal anymore..
    $("#edit-deck-toggle").click(() => {
        $("#editDeckModal").modal("show");
    });

    $("#configure-studyplan-toggle").click(() => {
        $("#configureStudyPlan").modal("show");
    });

    // Current card face; tracks the face to be synchronize flipping front and back faces
    var face = "front";

    // Flip card action
    $("#flip-card-btn, .flip-card").click(() => {
        if (face == "front") {
            $(".flip-card-inner").css({ transform: "rotateY(180deg)" });
            face = "back";
            $("#card-legend-text").css({ color: "#fff" });
        } else if (face == "back") {
            $(".flip-card-inner").css({ transform: "none" });
            face = "front";
            $("#card-legend-text").css({ color: "#223843" });
        }
        $("#card-legend-text").text(face).fadeIn(0.6);
    });

    // Mark Known / Unknown cards
    $("#known-card, #unknown-card").click(() => {
        // Fetch next card in the deck

        $(".flip-card-front").text(Math.random().toString(36).substring(7));
        $(".flip-card-back").text(Math.random().toString(36).substring(7));
        let el = $(".flip-card-inner").addClass(
            "animate__animated animate__slideInRight"
        );
        setTimeout(() => {
            el.removeClass("animate__animated animate__slideInRight");
        }, 500);
    });

    // Add cards to a deck
    var formsetCount = 1;
    var extra_formsets = 0;
    $("#add-deck-card-formset").click(() => {
        let addFormsetBtn = $("#add-deck-card-formset").parent();
        extra_formsets += 1;
        let formset = `
        <div class="form-group">
            <hr style="color: #dee2e6; margin: 0;" class="mt-4 mb-2">
            <div class="row">
                <div class="col-md-6 mt-2">
                    <label for="front${formsetCount}">Front</label>
                    <textarea name="front${formsetCount}" class="form-control" id="front${formsetCount}" rows="2" required></textarea>
                </div>
                <div class="col-md-6 mt-2">
                    <label for="back${formsetCount}">Back</label>
                    <i onclick="removeFormset(event, this)" class="fa fa-times remove-card-formset float-right text-danger"></i>
                    <textarea name="back${formsetCount}" class="form-control" id="back${formsetCount}" rows="2" required></textarea>
                </div>
            </div>
        </div>`;
        formsetCount += 1;
        $(formset).insertBefore(addFormsetBtn);
    });

    // Doughnut Charts

    const decksDt = dtInitWrapper("#decksDt", "decks");
    const cardsDt = dtInitWrapper("#allCardsDt", "cards");
    const plansDt = dtInitWrapper("#plansDt", "study plans");
    $("#main-content").fadeIn("slow");
});

// Remove deck card formset
function removeFormset(e, formset) {
    $(formset).parent().parent().parent().remove();
}

// Edit Deck within the deck dt
function toggleDeckDtModal(deck_id) {
    $.ajax({
        type: "POST",
        url: `/deck/${deck_id}`,
        data: null,
        contentType: false,
        processData: false,
        success: (data) => {
            // Populate edit deck form..
            $("#editDeckDtModal").find("#name").val(data.name);
            $("#editDeckDtModal").find("#description").val(data.description);

            // Bind the onSubmit event listener of the editmodal form to
            // editItem() method..
            $("#editDeckDtFormSubmit").on("click", function () {
                editItem(
                    new SubmitEvent($("#editDeckDtForm")),
                    $("#editDeckDtForm")[0],
                    "Deck",
                    "POST",
                    `/deck/${data.id}/edit`,
                    "/decks"
                );
            });

            $("#editDeckDtModal").modal("show");
        },
        error: (data) => {
            Toast.fire({
                icon: "error",
                title: `Failed to retrieve Deck. Try again later`,
            });
        },
    });
}

// Generic editItem wrapper method
function editItem(e, form, item, method, target_url, success_url = null) {
    e.preventDefault();
    formData = new FormData(form);

    $.ajax({
        type: method,
        url: target_url,
        data: formData,
        contentType: false,
        processData: false,
        success: (data) => {
            if (data == "Success") {
                Toast.fire({
                    icon: "success",
                    title: `${item} updated successfully`,
                }).then(() => {
                    if (success_url !== null) {
                        location.replace(success_url);
                    }
                });
            } else {
                Toast.fire({
                    icon: "error",
                    title: `Failed to update ${item}. Try again later`,
                });
            }
        },
        error: (data) => {
            Toast.fire({
                icon: "error",
                title: `Failed to update ${item}. Try again later`,
            });
        },
    });
}

// Datatables initializer wrapper
function dtInitWrapper(id, name) {
    let dt = $(id).DataTable({
        dom:
            '<"div custom-dt" rt> <"row" <"col-md-12 col-lg-6" i> <"col-md-12 col-lg-6" p>>',
        // "responsive": {
        //     "details": {
        //         renderer: function (api, rowIdx, columns) {
        //             var data = $.map(columns, function (col, i) {

        //                 // Hacky way of hiding the index column completely for now
        //                 // The index value seems not to be evaluated when responsive dt is rendered..
        //                 if (col.columnIndex == 0) {
        //                     return ''
        //                 }
        //                 return col.hidden ?
        //                     `<li data-dtr-index="${i}" data-dt-row="${col.rowIndex}" data-dt-column="${col.columnIndex}">
        //                         <span class="dtr-title">${col.title}</span>
        //                         <span class="dtr-data">${col.data}</span>
        //                     </li>` : '';
        //             }).join('');

        //             data = `
        //             <ul class="dtr-details" data-dtr-index="${rowIdx}">
        //             ${data}
        //             </ul>`;
        //             return data ? $('<table/>').append(data) : false;
        //         }
        //     }
        // },
        columnDefs: [
            {
                orderable: false,
                targets: 0,
                searcheable: false,
                className: "dtr-control",
                render: function (data, type, full, meta) {
                    return `
                <div class="custom-control custom-checkbox">
                    <input type="checkbox" class="custom-control-input" id="dataCheck${
                        meta.row
                    }" name="id[]" value="${$("<div/>").text(meta.row).html()}">
                    <label class="custom-control-label" for="dataCheck${
                        meta.row
                    }"></label>
                </div> `;
                },
            },
        ],
        order: [[1, "asc"]],
        language: {
            emptyTable: `<div class="text-center">
                <img id="no-data-img" src="/static/img/assets/no-data.svg" style="width: 11rem" alt="no ${name} to show">
                <p class="text-muted">No ${name} to show</p>
            </div>`,
            zeroRecords: `<div class="text-center">
                <img id="no-data-img" src="/static/img/assets/no-data.svg" style="width: 11rem" alt="no ${name} to show">
                <p class="text-muted">No ${name} to show</p>
            </div>`,
            info: `Showing _END_ of _TOTAL_ ${name}`,
            infoEmpty: `Showing 0 of 0 ${name}`,
            infoFiltered: ``,
            lengthMenu: `Show _MENU_ ${name}`,
            loadingRecords: "Loading...",
            processing: "Processing...",
            search: "Search:",
            paginate: {
                first: "First",
                last: "Last",
                next: "Next",
                previous: "Prev",
            },
            aria: {
                sortAscending: ": activate to sort column ascending",
                sortDescending: ": activate to sort column descending",
            },
        },
    });

    // Handle click on checkbox to set state of "Select all" control
    $(".custom-dt").on(
        "change",
        'input[type="checkbox"][name="id[]"]',
        function () {
            // Get the target row and select it or deselect
            var target = $(this).parents().eq(2);
            if (this.checked) {
                dt.row(target).select();
            } else {
                dt.row(target).deselect();
            }
            // getSelectedChekboxes(dt);
        }
    );

    $("#dt-select-all").click(function () {
        var rows = dt
            .rows({
                search: "applied",
            })
            .nodes();

        // Check/uncheck while also selecting(With regards to the dt..)
        // checkboxes for all rows in the table
        if (!this.checked) {
            dt.rows().deselect();
            $('input[type="checkbox"]', rows).prop("checked", false);
            return;
        } else {
            dt.rows().select();
            $('input[type="checkbox"]', rows).prop("checked", true);
            return;
        }
    });

    dt.on("select deselect", function (e, dt, type, indexes) {
        const selected = dt.rows({
            selected: true,
        });
        const unselected = dt
            .rows({
                selected: false,
            })
            .count();

        if (selected.count() > 0) {
            var ids = [];
            // console.log(selected[0]);
            selected[0].forEach(function (r) {
                let data = dt.row(r).data();
                if (data) {
                    ids.push(Number(data[data.length - 1]));
                }
            });
            $("#selected_count").html(
                `
                <span class="mr-2">${selected.count()} Selected</span>
                <a href="#" id="delete_selected">
                <button class="btn btn-sm btn-outline-danger delete-selected-btn">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-trash">
                    <polyline points="3 6 5 6 21 6"></polyline>
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                </svg>
                Delete
                </button>   
                </a>
                `
            );

            $("#delete_selected").click(function () {
                Swal.fire({
                    title: "Confirm Decks deletion!",
                    text: `${selected.count()} deck(s) will be deleted permanently.`,
                    icon: "warning",
                    showCancelButton: true,
                    cancelButtonColor: "#3085d6",
                    confirmButtonColor: "#d33",
                    confirmButtonText: "Delete them",
                });
            });
        } else if (selected.count() == 0) {
            $("#selected_count").html(``);
        }
        // , function (r) {
        //     ids.push(r[-1]);
        // })
        // console.log(dt.row(selected[0]).data());
    });

    // Custom search input.
    $("#datatableSearch").keyup(function () {
        dt.search($(this).val()).draw();
    });

    // $("#some-el").on("change", function () {
    //     var $this = $(this),
    //         elVal = $this.val(),
    //         targetColumnIndex = $this.data('target-col-index');
    //     dt.column(targetColumnIndex).search(elVal).draw();
    // });
    $("#deck_name").on("change", function () {
        var $this = $(this),
            elVal = $this.val();
        if (elVal == null) {
            dt.column(3).search("").draw();
        } else {
            dt.column(3).search(elVal).draw();
        }
    });

    // dt.column(3).search(10).draw();
    // $("#datableSearch").on("search", function () {
    //     console.log("Searching...");
    //     dt.search('').draw();
    // })
}

// A Swal mixin for timed alerts.
const Toast = Swal.mixin({
    toast: true,
    position: "top-end",
    showConfirmButton: false,
    timer: 3000,
    timerProgressBar: true,
    onOpen: (toast) => {
        toast.addEventListener("mouseenter", Swal.stopTimer);
        toast.addEventListener("mouseleave", Swal.resumeTimer);
    },
});

function deleteDeck(deck_id) {
    Swal.fire({
        title: "Confirm Deck deletion!",
        text: "This deck will be deleted permanently.",
        icon: "warning",
        showCancelButton: true,
        cancelButtonColor: "#3085d6",
        confirmButtonColor: "#d33",
        confirmButtonText: "Delete it",
    }).then(function (result) {
        if (result.value) {
            $.ajax({
                method: "POST",
                url: `/deck/${deck_id}/delete`,
            })
                .done(function () {
                    Swal.fire({
                        text: "Deck deleted succesfully",
                        icon: "success",
                    }).then(() => {
                        location.reload();
                    });
                })
                .fail(() => {
                    Toast.fire({
                        icon: "error",
                        title: "Failed to delete deck. Try again later",
                    });
                });
        }
    });
}

// Basic Wrapper to ease the handling of simple Ajax requests
function handleAjax(e, form, item, method, target_url, success_url = null) {
    e.preventDefault();
    var formData = new FormData(form);

    // Handle Deck cards formsets
    // Loop through each textarea, and construct a card object with
    // its front and back by simply checking which is first i.e the front
    // value will always be in an index divisible by 2, so the next textarea automatically is back
    // Consecutively check each 'prevCard' object for front and back value, append this to cards array
    // and empty it else continue to the next textarea.
    if ($(form).attr("id") == "add-deck-cards-form") {
        var cards = [];
        prevCard = {};
        var cardFormSets = $(form).find("textarea");
        for (var i = 0; i < cardFormSets.length; i++) {
            if (i % 2 == 0) {
                prevCard["front"] = $(cardFormSets[i]).val();
            } else {
                prevCard["back"] = $(cardFormSets[i]).val();
            }
            if (
                prevCard.hasOwnProperty("front") &&
                prevCard.hasOwnProperty("back")
            ) {
                cards.push(prevCard);
                prevCard = {};
            }
            // console.log($(cardFormSets[i]).val());
        }
        // The current formData will be JSON serialized cards array..
        formData = JSON.stringify(cards);
    }

    // Override see_solved check-box to post boolean values
    if (form.id === "create-plan-form") {
        if (formData.has("see_solved")) {
            formData.set("see_solved", true);
        } else {
            formData.set("see_solved", false);
        }
    }

    $.ajax({
        type: method,
        url: target_url,
        data: formData,
        contentType: false,
        processData: false,
        success: (data) => {
            if (data == "Success") {
                Toast.fire({
                    icon: "success",
                    title: `${item} created successfully`,
                }).then(() => {
                    if (success_url !== null) {
                        location.replace(success_url);
                    }
                });
            } else {
                Toast.fire({
                    icon: "error",
                    title: `Failed to create ${item}: ${data}`,
                });
            }
        },
        error: (data) => {
            Toast.fire({
                icon: "error",
                title: `Failed to create ${item}. Try again later`,
            });
        },
    });
}

// Select2 Lookup data initializer
function select2Lookup(selector, placeholder = "Select an option") {
    console.log(selector);
    $(selector).select2({
        placeholder: placeholder,
        allowClear: true,
    });
}
