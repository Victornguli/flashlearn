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


// Datatables initializer wrapper
function dtInitWrapper(id, name) {
    let dt = $(id).DataTable({
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
            "className": 'select-checkbox',
            "targets": 0
        }],
        "select": {
            "style": 'multi',
            "selector": 'td:first-child'
        },
        "order": [
            [1, 'asc']
        ],
        "language": {
            "emptyTable": `You do have not created any ${name} yet.`,
            "zeroRecords": `No matching ${name} found. Try another set of filters`,
            "info": `Showing _START_ to _END_ of _TOTAL_ ${name}`,
            "infoEmpty": `Showing 0 to 0 of 0 ${name}`,
            "infoFiltered": `(filtered from _MAX_ total ${name})`,
            "lengthMenu": `Show _MENU_ ${name}`,
            "loadingRecords": "Loading...",
            "processing": "Processing...",
            "search": "Search:",
            "paginate": {
                "first": "First",
                "last": "Last",
                "next": "Next",
                "previous": "Previous"
            },
            "aria": {
                "sortAscending": ": activate to sort column ascending",
                "sortDescending": ": activate to sort column descending"
            }
        }
    });

    // dt.on('order.dt search.dt', function () {
    //     dt.column(0, {
    //         search: 'applied',
    //         order: 'applied'
    //     }).nodes().each(function (cell, i) {
    //         cell.innerHTML = i + 1;
    //     });
    // }).draw();
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