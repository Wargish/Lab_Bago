

// Image Load

document.getElementById('id_image').addEventListener('change', function(event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const img = document.getElementById('image-preview');
            img.src = e.target.result;
            img.style.display = 'block';
        }
        reader.readAsDataURL(file);
    }
});


// Sweet alert Generar Informe
document.querySelector('form').addEventListener('submit', function(event) {
    let form = event.target;
    let valid = true;

    form.querySelectorAll('.md-form').forEach(function(div) {
        let input = div.querySelector('input, textarea, select');
        if (!input.value) {
            valid = false;
            div.querySelector('.invalid-feedback').style.display = 'block';
        } else {
            div.querySelector('.invalid-feedback').style.display = 'none';
        }
    });

    event.preventDefault();

    if (valid) {
        Swal.fire({
            icon: "success",
            title: "Se Cargo exitosamente el informe",
            text: "Un tecnico respondera a la brevedad posible.",
        }).then(() => {
            form.submit();
        });
    } else {
        Swal.fire({
            icon: "error",
            title: "Oops...",
            text: "Por favor rellena todos los campos.",
        });
    }
});

// Sweet alert Generar Reporte










// Sweet alert Generar Feedback


















// Modal Feedback
document.addEventListener('DOMContentLoaded', function() {
    $('#feedbackModal').on('show.bs.modal', function (event) {
        var button = $(event.relatedTarget);
        var tareaId = button.data('tarea-id');
        var modal = $(this);
        modal.find('#tareaIdInput').val(tareaId);
    });

    $('#conforme').on('change', function() {
        if ($(this).val() === 'False') {
            $('#comentarioGroup').show();
        } else {
            $('#comentarioGroup').hide();
            $('#comentario').val('Felicitaciones por completar la tarea.');
        }
    });

    // Handle form submission with SweetAlert2
    document.getElementById('feedbackForm').addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent the default form submission

        const conforme = document.getElementById('conforme').value;
        const comentario = document.getElementById('comentario').value;

        if (conforme === 'False' && comentario.trim() === '') {
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'Por favor, proporciona un comentario si rechazas el trabajo.',
            });
        } else {
            Swal.fire({
                title: '¿Estás seguro?',
                text: "No podrás revertir esta acción.",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#3085d6',
                cancelButtonColor: '#d33',
                confirmButtonText: 'Sí, enviar feedback'
            }).then((result) => {
                if (result.isConfirmed) {
                    // Submit the form
                    event.target.submit();
                }
            });
        }
    });
});