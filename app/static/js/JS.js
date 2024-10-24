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

