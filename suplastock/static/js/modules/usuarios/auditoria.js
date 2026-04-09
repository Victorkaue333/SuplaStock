(function () {
    'use strict';

    function resetPasswordVisibilityState(container) {
        if (!container) {
            return;
        }

        container.querySelectorAll('[data-toggle-password]').forEach(function (button) {
            const targetId = button.getAttribute('data-toggle-password');
            const input = targetId ? document.getElementById(targetId) : null;
            if (input) {
                input.setAttribute('type', 'password');
            }

            const icon = button.querySelector('i');
            if (icon) {
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            }
            button.setAttribute('aria-label', 'Mostrar senha');
        });
    }

    function setupCreateUserModal() {
        const createModal = document.getElementById('modalNovoUsuario');
        const createForm = createModal ? createModal.querySelector('form') : null;
        if (!createModal) {
            return;
        }

        createModal.addEventListener('show.bs.modal', function () {
            const preserveOnOpen = createModal.dataset.preserveOnOpen === '1';
            if (createForm && !preserveOnOpen) {
                createForm.reset();
            }

            resetPasswordVisibilityState(createModal);

            if (preserveOnOpen) {
                createModal.dataset.preserveOnOpen = '0';
            }
        });

        if (createModal.dataset.preserveOnOpen === '1' && window.bootstrap && window.bootstrap.Modal) {
            const modalInstance = window.bootstrap.Modal.getOrCreateInstance(createModal);
            modalInstance.show();
        }
    }

    function setupEditUserModal() {
        const editModal = document.getElementById('modalEditarUsuario');
        const editForm = document.getElementById('formEditarUsuario');
        if (!editModal || !editForm) {
            return;
        }

        const nomeInput = document.getElementById('editNomeCompleto');
        const usernameInput = document.getElementById('editUsername');
        const emailInput = document.getElementById('editEmail');
        const nivelInput = document.getElementById('editNivelAcesso');
        const ativoInput = document.getElementById('editUsuarioAtivo');

        editModal.addEventListener('show.bs.modal', function (event) {
            const trigger = event.relatedTarget;
            if (!trigger) {
                return;
            }

            editForm.setAttribute('action', trigger.getAttribute('data-update-url') || '');
            if (nomeInput) nomeInput.value = trigger.getAttribute('data-usuario-nome') || '';
            if (usernameInput) usernameInput.value = trigger.getAttribute('data-usuario-username') || '';
            if (emailInput) emailInput.value = trigger.getAttribute('data-usuario-email') || '';
            if (nivelInput) nivelInput.value = trigger.getAttribute('data-usuario-nivel') || 'vendedor';
            if (ativoInput) ativoInput.checked = (trigger.getAttribute('data-usuario-ativo') === '1');
        });
    }

    function setupResetPasswordModal() {
        const resetModal = document.getElementById('modalResetSenha');
        const resetForm = document.getElementById('formResetSenha');
        const usuarioNome = document.getElementById('resetSenhaUsuarioNome');
        const passwordInputs = [
            document.getElementById('resetNovaSenhaInput'),
            document.getElementById('resetConfirmarSenhaInput')
        ];
        if (!resetModal || !resetForm) {
            return;
        }

        resetModal.addEventListener('show.bs.modal', function (event) {
            const trigger = event.relatedTarget;
            if (!trigger) {
                return;
            }

            resetForm.setAttribute('action', trigger.getAttribute('data-reset-url') || '');
            if (usuarioNome) {
                usuarioNome.textContent = trigger.getAttribute('data-usuario-nome') || trigger.getAttribute('data-usuario-username') || '-';
            }

            resetForm.reset();
            passwordInputs.forEach(function (input) {
                if (input) {
                    input.setAttribute('type', 'password');
                }
            });
            resetPasswordVisibilityState(resetModal);
        });

        resetForm.addEventListener('submit', function (event) {
            const senha = (resetForm.querySelector('input[name="nova_senha"]') || {}).value || '';
            const confirmar = (resetForm.querySelector('input[name="confirmar_senha"]') || {}).value || '';
            if (senha && senha !== confirmar) {
                event.preventDefault();
                window.alert('A confirmação da nova senha não confere.');
            }
        });
    }

    function setupDeleteUserModal() {
        const deleteModal = document.getElementById('modalDeletarUsuario');
        const deleteForm = document.getElementById('formDeletarUsuario');
        if (!deleteModal || !deleteForm) {
            return;
        }

        const nomeEl = document.getElementById('deleteUsuarioNome');
        const usernameEl = document.getElementById('deleteUsuarioUsername');
        const nivelEl = document.getElementById('deleteUsuarioNivel');

        deleteModal.addEventListener('show.bs.modal', function (event) {
            const trigger = event.relatedTarget;
            if (!trigger) {
                return;
            }

            deleteForm.setAttribute('action', trigger.getAttribute('data-delete-url') || '');
            if (nomeEl) nomeEl.textContent = trigger.getAttribute('data-usuario-nome') || '-';
            if (usernameEl) usernameEl.textContent = trigger.getAttribute('data-usuario-username') || '-';
            if (nivelEl) nivelEl.textContent = trigger.getAttribute('data-usuario-nivel') || '-';
        });
    }

    function setupPasswordVisibilityToggles() {
        document.querySelectorAll('[data-toggle-password]').forEach(function (button) {
            button.addEventListener('click', function () {
                const targetId = button.getAttribute('data-toggle-password');
                const input = targetId ? document.getElementById(targetId) : null;
                if (!input) {
                    return;
                }

                const isPassword = input.getAttribute('type') === 'password';
                input.setAttribute('type', isPassword ? 'text' : 'password');

                const icon = button.querySelector('i');
                if (icon) {
                    icon.classList.toggle('fa-eye', !isPassword);
                    icon.classList.toggle('fa-eye-slash', isPassword);
                }

                button.setAttribute('aria-label', isPassword ? 'Ocultar senha' : 'Mostrar senha');
            });
        });
    }

    document.addEventListener('DOMContentLoaded', function () {
        setupCreateUserModal();
        setupEditUserModal();
        setupResetPasswordModal();
        setupDeleteUserModal();
        setupPasswordVisibilityToggles();
    });
})();
