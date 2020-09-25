$(document).ready(function () {
    // Init Select2 Options
    $('.select2').select2({
        placeholder: "Select an option",
        allowClear: true
    });

    const decksDt = dtInitWrapper("#decksDt", "decks");
    const cardsDt = dtInitWrapper("#cardsDt", "cards");
    const plansDt = dtInitWrapper("#plansDt", "study plans");
});


// Retrieve checked rows..
function getSelectedChekboxes(dt) {
    var counter = 1;
    dt.$('input[type="checkbox"]').each(function () {
        // If checkbox is checked
        if (this.checked) {
            // Create a hidden element
            counter += 1;
        }
    });
}


// Datatables initializer wrapper
function dtInitWrapper(id, name) {
    let dt = $(id).DataTable({
        "dom": 'rt <"row" <"col-md-12 col-lg-6" i> <"col-md-12 col-lg-6" p>>',
        "responsive": {
            "details": {
                renderer: function (api, rowIdx, columns) {
                    var data = $.map(columns, function (col, i) {

                        // Hacky way of hiding the index column completely for now
                        // The index value seems not to be evaluated when responsive dt is rendered..
                        if (col.columnIndex == 0) {
                            return ''
                        }
                        return col.hidden ?
                            `<li data-dtr-index="${i}" data-dt-row="${col.rowIndex}" data-dt-column="${col.columnIndex}">
                                <span class="dtr-title">${col.title}</span>
                                <span class="dtr-data">${col.data}</span>
                            </li>` : '';
                    }).join('');

                    data = `
                    <ul class="dtr-details" data-dtr-index="${rowIdx}">
                    ${data}
                    </ul>`;
                    return data ? $('<table/>').append(data) : false;
                }
            }
        },
        "columnDefs": [{
            "orderable": false,
            "targets": 0,
            "searcheable": false,
            "className": "dtr-control",
            'render': function (data, type, full, meta) {
                return `
                <div class="custom-control custom-checkbox">
                    <input type="checkbox" class="custom-control-input" id="dataCheck${meta.row}" name="id[]" value="${$('<div/>').text(meta.row).html()}">
                    <label class="custom-control-label" for="dataCheck${meta.row}"></label>
                </div> `
            }
        }],
        "order": [
            [1, 'asc']
        ],
        "language": {
            "emptyTable": `<div class="text-center">
                <img id="no-data-img" src="/static/img/assets/no-data.svg" style="width: 11rem" alt="no ${name} to show">
                <p class="text-muted">No ${name} to show</p>
            </div>`,
            "zeroRecords": `<div class="text-center">
                <img id="no-data-img" src="/static/img/assets/no-data.svg" style="width: 11rem" alt="no ${name} to show">
                <p class="text-muted">No ${name} to show</p>
            </div>`,
            "info": `Showing _END_ of _TOTAL_ ${name}`,
            "infoEmpty": `Showing 0 of 0 ${name}`,
            "infoFiltered": ``,
            "lengthMenu": `Show _MENU_ ${name}`,
            "loadingRecords": "Loading...",
            "processing": "Processing...",
            "search": "Search:",
            "paginate": {
                "first": "First",
                "last": "Last",
                "next": "Next",
                "previous": "Prev"
            },
            "aria": {
                "sortAscending": ": activate to sort column ascending",
                "sortDescending": ": activate to sort column descending"
            }
        }
    });

    // Handle click on checkbox to set state of "Select all" control
    $('.custom-dt').on('change', 'input[type="checkbox"][name="id[]"]', function () {
        // Get the target row and select it or deselect
        var target = $(this).parents().eq(2);
        if (this.checked) {
            dt.row(target).select();
        } else {
            dt.row(target).deselect();
        }
        // getSelectedChekboxes(dt);
    });

    $('#dt-select-all').click(function () {
        var rows = dt.rows({
            'search': 'applied'
        }).nodes();

        // Check/uncheck while also selecting(With regards to the dt..) 
        // checkboxes for all rows in the table
        if (!this.checked) {
            dt.rows().deselect();
            $('input[type="checkbox"]', rows).prop('checked', false);
            return;
        } else {
            dt.rows().select();
            $('input[type="checkbox"]', rows).prop('checked', true);
            return;
        }
    });

    // dt.on('select deselect', function (e, dt, type, indexes) {
    //     const selected = dt.rows({
    //         selected: true
    //     }).count();
    //     const unselected = dt.rows({
    //         selected: false
    //     }).count();
    //     el = $("#dt-select-all").get(0);
    //     if (el.checked && ('indeterminate' in el)) {
    //         // Set visual state of "Select all" control
    //         // as 'indeterminate'
    //         el.indeterminate = true;
    //     }
    // });

    // Custom search input.
    $('#datatableSearch').keyup(function () {
        console.log($(this).val());
        dt.search($(this).val()).draw();
    })
    $("#datableSearch").on("search", function () {
        console.log("Searching...");
        dt.search('').draw();
    })
}


// A Swal mixin for timed alerts.
const Toast = Swal.mixin({
    toast: true,
    position: 'top-end',
    showConfirmButton: false,
    timer: 3000,
    timerProgressBar: true,
    onOpen: (toast) => {
        toast.addEventListener('mouseenter', Swal.stopTimer)
        toast.addEventListener('mouseleave', Swal.resumeTimer)
    }
})

function deleteDeck(deck_id) {
    console.log(deck_id);
    Swal.fire({
        title: 'Confirm Deck deletion!',
        text: 'This deck will be deleted permanently.',
        icon: 'warning',
        showCancelButton: true,
        cancelButtonColor: '#3085d6',
        confirmButtonColor: '#d33',
        confirmButtonText: 'Delete it'
    }).then(function (result) {
        if (result.value) {
            $.ajax({
                    method: 'POST',
                    url: `/deck/${deck_id}/delete`
                }).done(function () {
                    Swal.fire({
                        text: 'Deck deleted succesfully',
                        icon: 'success'
                    }).then(() => {
                        location.reload();
                    })
                })
                .fail(() => {
                    Toast.fire({
                        icon: 'error',
                        title: 'Failed to delete deck. Try again later'
                    })
                })
        }
    });
}

// Basic Wrapper to ease the handling of simple Ajax requests
function handleAjax(e, form, item, method, target_url, success_url = null) {
    e.preventDefault();
    var formData = new FormData(form);

    // Override see_solved check-box to post boolean values
    if (form.id === 'create-plan-form') {
        if (formData.has('see_solved')) {
            formData.set('see_solved', true);
        } else {
            formData.set('see_solved', false);
        }
    }

    $.ajax({
        type: method,
        url: target_url,
        data: formData,
        contentType: false,
        processData: false,
        success: (data) => {
            if (data == 'Success') {
                Toast.fire({
                    icon: 'success',
                    title: `${item} created successfully`,
                }).then(() => {
                    if (success_url !== null) {
                        location.replace(success_url);
                    }
                })
            } else {
                Toast.fire({
                    icon: 'error',
                    title: `Failed to create ${item}: ${data}`
                })
            }

        },
        error: (data) => {
            Toast.fire({
                icon: 'error',
                title: `Failed to create ${item}. Try again later`
            })
        }
    });
}