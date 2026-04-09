(() => {
    const STORAGE_KEY = 'suplastock_login_identifier';
    const form = document.getElementById('loginForm');
    const usernameField = document.getElementById('usernameField');
    const rememberCheckbox = document.getElementById('rememberMeCheckbox');
    const passwordField = document.getElementById('passwordField');
    const togglePasswordButton = document.getElementById('togglePasswordButton');

    if (!form || !usernameField || !rememberCheckbox) {
        return;
    }

    const readRememberedIdentifier = () => {
        try {
            return window.localStorage.getItem(STORAGE_KEY) || '';
        } catch (error) {
            return '';
        }
    };

    const saveRememberedIdentifier = (identifier) => {
        try {
            window.localStorage.setItem(STORAGE_KEY, identifier);
        } catch (error) {
            // Silent failure to keep login flow stable.
        }
    };

    const clearRememberedIdentifier = () => {
        try {
            window.localStorage.removeItem(STORAGE_KEY);
        } catch (error) {
            // No-op.
        }
    };

    const rememberedIdentifier = readRememberedIdentifier();
    const currentValue = (usernameField.value || '').trim();

    // Prefill only when backend did not return a value (e.g. failed login).
    if (!currentValue && rememberedIdentifier) {
        usernameField.value = rememberedIdentifier;
    }

    if (rememberedIdentifier) {
        rememberCheckbox.checked = true;
    }

    rememberCheckbox.addEventListener('change', () => {
        if (!rememberCheckbox.checked) {
            clearRememberedIdentifier();
        }
    });

    form.addEventListener('submit', () => {
        const identifier = (usernameField.value || '').trim();

        if (rememberCheckbox.checked && identifier) {
            // Security: store only username/email, never password.
            saveRememberedIdentifier(identifier);
        } else {
            clearRememberedIdentifier();
        }
    });

    if (passwordField && togglePasswordButton) {
        togglePasswordButton.addEventListener('click', () => {
            const isHidden = passwordField.getAttribute('type') === 'password';
            passwordField.setAttribute('type', isHidden ? 'text' : 'password');

            const icon = togglePasswordButton.querySelector('i');
            if (icon) {
                icon.classList.toggle('fa-eye', !isHidden);
                icon.classList.toggle('fa-eye-slash', isHidden);
            }

            togglePasswordButton.setAttribute(
                'aria-label',
                isHidden ? 'Ocultar senha' : 'Mostrar senha',
            );
        });
    }
})();

