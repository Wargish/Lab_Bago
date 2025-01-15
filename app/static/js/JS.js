// Modal Roles Logic
document.querySelectorAll('.dropdown-item').forEach(item => {
    item.addEventListener('click', function (event) {
        const action = this.getAttribute('data-action');
        if (!action) return; // Si no hay acción, no hacer nada

        event.preventDefault(); // Evita el comportamiento predeterminado del botón

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
            case 'modify':
                    const userEmail = this.getAttribute('data-email');
                    modalTitle.textContent = `Modificar usuario ${username}`;
                    modalBody.innerHTML = `
                        <form id="modifyUserForm">
                            <div class="mb-3">
                                <label for="username" class="form-label">Username</label>
                                <input type="text" class="form-control" id="username" name="username" value="${username}">
                            </div>
                            <div class="mb-3">
                                <label for="email" class="form-label">Correo</label>
                                <input type="email" class="form-control" id="email" name="email" value="${userEmail}">
                            </div>
                            <div class="mb-3">
                                <label for="password" class="form-label">Contraseña</label>
                                <input type="password" class="form-control" id="password" name="password">
                                <div class="form-text text-muted">
                                    La contraseña debe contener al menos:
                                    <ul>
                                        <li>8 caracteres</li>
                                        <li>Una mayúscula</li>
                                        <li>Un carácter especial (!@#$%^&*)</li>
                                    </ul>
                                </div>
                                <div id="passwordError" class="invalid-feedback"></div>
                            </div>
                            <input type="hidden" name="user_id" value="${userId}">
                            <input type="hidden" name="action" value="modify_user">
                        </form>
                    `;
                    modalActionButton.textContent = 'Guardar Cambios';
                    modalActionButton.onclick = function () {
                        const form = document.getElementById('modifyUserForm');
                        const password = form.querySelector('#password').value;
                        
                        // Solo validar si se ingresó una contraseña
                        if (password) {
                            const passwordRegex = /^(?=.*[A-Z])(?=.*[.!@#$%^&*.])[A-Za-z\d.!@#$%^&*.]{8,}$/;
                            if (!passwordRegex.test(password)) {
                                const passwordInput = form.querySelector('#password');
                                passwordInput.classList.add('is-invalid');
                                const errorDiv = form.querySelector('#passwordError');
                                errorDiv.textContent = 'La contraseña debe tener al menos 8 caracteres, una mayúscula y un carácter especial';
                                return;
                            }
                        }
                
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
                                console.error('Error al modificar el usuario');
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