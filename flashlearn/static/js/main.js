$(document).ready(function () {
    // Init Select2 Options
    $('.select2').select2({
        placeholder: "Select an option",
        allowClear: true
    });

    var decksDt = $('#decks').DataTable({
        "columnDefs": [{
            "searchable": false,
            "orderable": false,
            "targets": 0
        }],
        "order": [
            [1, 'asc']
        ],
        "language": {
            "emptyTable": "You do not have created any deck yet.",
            "zeroRecords": "No matching decks found. Try another set of filters",
            "info": "Showing _START_ to _END_ of _TOTAL_ decks",
            "infoEmpty": "Showing 0 to 0 of 0 decks",
            "infoFiltered": "(filtered from _MAX_ total decks)",
            "lengthMenu": "Show _MENU_ decks",
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

    decksDt.on('order.dt search.dt', function () {
        decksDt.column(0, {
            search: 'applied',
            order: 'applied'
        }).nodes().each(function (cell, i) {
            cell.innerHTML = i + 1;
        });
    }).draw();
});

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

$("#create-deck-form").submit(function (e) {

    e.preventDefault();

    var form = $(this);
    $.ajax({
        type: "POST",
        url: '/deck',
        data: form.serialize(),
        success: (data) => {
            Toast.fire({
                icon: 'success',
                title: 'Deck created successfully'
            }).then(() => {
                location.replace('/decks');
            })
        },
        error: (data) => {
            Toast.fire({
                icon: 'error',
                title: 'Failed to create deck. Try again later'
            })
        }
    });
});