// SweetAlert function
function showSweetAlert(icon, title, text, confirmButtonText = 'Aceptar') {
    return Swal.fire({
        icon: icon,
        title: title,
        text: text,
        confirmButtonText: confirmButtonText
    });
}

document.addEventListener('DOMContentLoaded', function () {
    

    // Image Preview Logic
    const imageInput = document.getElementById('id_image');
    if (imageInput) {
        imageInput.addEventListener('change', function(event) {
            const file = event.target.files[0];
            if (file) {
                const fileType = file.type.split('/')[0];
                if (fileType === 'image') {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        const img = document.getElementById('image-preview');
                        img.src = e.target.result;
                        img.style.display = 'block';
                    };
                    reader.readAsDataURL(file);
                } else {
                    showSweetAlert('error', 'Tipo de archivo no válido', 'Por favor selecciona una imagen.', 'Aceptar');
                    imageInput.value = ''; // Limpiar el campo
                    imagePreview.style.display = 'none'; // Ocultar imagen previa
                }
            }
        });
    }


    // Modal Roles Logic
    document.querySelectorAll('.dropdown-item').forEach(item => {
        item.addEventListener('click', function () {
            const action = this.getAttribute('data-action');
            const username = this.getAttribute('data-username');
            const userId = this.getAttribute('data-user-id');
            const modalTitle = document.getElementById('modalTitle');
            const modalBody = document.getElementById('modalBody');
            const modalActionButton = document.getElementById('modalActionButton');

            switch (action) {
                case 'change_role':
                    modalTitle.textContent = `Cambiar rol de ${username}`;
                    modalBody.innerHTML = `
                        <form id="changeRoleForm">
                            <div class="mb-3">
                                <label for="roleSelect" class="form-label">Selecciona un nuevo rol</label>
                                <select class="form-select" id="roleSelect" name="role">
                                    <option value="Operario">Operario</option>
                                    <option value="Técnico">Técnico</option>
                                    <option value="Externo">Externo</option>
                                    <option value="Supervisor">Supervisor</option>
                                </select>
                            </div>
                            <input type="hidden" name="user_id" value="${userId}">
                            <input type="hidden" name="action" value="change_role">
                        </form>
                    `;
                    modalActionButton.textContent = 'Guardar Cambios';
                    modalActionButton.onclick = function () {
                        const form = document.getElementById('changeRoleForm');
                        const formData = new FormData(form);
                        fetch('/auth/roles/', {
                            method: 'POST',
                            body: formData,
                            headers: {
                                'X-CSRFToken': getCookie('csrftoken')
                            }
                        }).then(response => {
                            if (response.ok) {
                                location.reload();
                            } else {
                                console.error('Error al cambiar el rol');
                            }
                        });
                    };
                    break;
                case 'delete':
                    modalTitle.textContent = `Eliminar usuario ${username}`;
                    modalBody.innerHTML = `<p>¿Estás seguro de que deseas eliminar a ${username}?</p>`;
                    modalActionButton.textContent = 'Eliminar';
                    modalActionButton.onclick = function () {
                        const formData = new FormData();
                        formData.append('user_id', userId);
                        formData.append('action', 'delete_user');
                        fetch('/auth/roles/', {
                            method: 'POST',
                            body: formData,
                            headers: {
                                'X-CSRFToken': getCookie('csrftoken')
                            }
                        }).then(response => {
                            if (response.ok) {
                                location.reload();
                            } else {
                                console.error('Error al eliminar el usuario');
                            }
                        });
                    };
                    break;
                    case 'assign_task':
                        modalTitle.textContent = `Asignar tarea a ${username}`;
                        const tareasSinTecnico = document.getElementById('tareasSinTecnico').children;
                        let options = '';
                        for (let tarea of tareasSinTecnico) {
                            const id = tarea.getAttribute('data-id');
                            const objetivo = tarea.getAttribute('data-objetivo');
                            options += `<option value="${id}">${objetivo}</option>`;
                        }
                        modalBody.innerHTML = `
                            <form id="assignTaskForm">
                                <div class="mb-3">
                                    <label for="taskSelect" class="form-label">Selecciona una tarea</label>
                                    <select class="form-select" id="taskSelect" name="task_id">
                                        ${options}
                                    </select>
                                </div>
                                <input type="hidden" name="user_id" value="${userId}">
                                <input type="hidden" name="action" value="assign_task">
                            </form>
                        `;
                        modalActionButton.textContent = 'Asignar Tarea';
                        modalActionButton.onclick = function () {
                            const form = document.getElementById('assignTaskForm');
                            const formData = new FormData(form);
                            fetch('/auth/roles/', {
                                method: 'POST',
                                body: formData,
                                headers: {
                                    'X-CSRFToken': getCookie('csrftoken')
                                }
                            }).then(response => {
                                if (response.ok) {
                                    location.reload();
                                } else {
                                    console.error('Error al asignar la tarea');
                                }
                            });
                        };
                        break;
            }

            const myModal = new bootstrap.Modal(document.getElementById('actionModal'));
            myModal.show();
        });
    });

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
