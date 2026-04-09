(function initializeAppFeedback() {
    const toastContainer = document.getElementById('app-toast-container');
    const confirmModalElement = document.getElementById('appConfirmModal');
    const confirmModalTitle = document.getElementById('appConfirmModalTitle');
    const confirmModalMessage = document.getElementById('appConfirmModalMessage');
    const confirmAcceptButton = document.getElementById('appConfirmAcceptButton');
    const confirmCancelButton = document.getElementById('appConfirmCancelButton');

    const DEFAULT_DELAY = 4500;
    const VARIANT_MAP = {
        success: 'success',
        info: 'info',
        warning: 'warning',
        error: 'danger',
        danger: 'danger'
    };

    const normalizeVariant = (level) => {
        const normalized = String(level || '')
            .toLowerCase()
            .split(/\s+/)
            .find((token) => Object.prototype.hasOwnProperty.call(VARIANT_MAP, token));
        return VARIANT_MAP[normalized] || 'info';
    };

    const getToastContainer = () => {
        if (toastContainer) {
            return toastContainer;
        }
        return null;
    };

    const showToast = (message, options = {}) => {
        const container = getToastContainer();
        const messageText = String(message || '').trim();
        const mergedOptions = typeof options === 'string'
            ? { variant: options }
            : options;
        const variant = normalizeVariant(mergedOptions.variant || 'info');
        const delay = Number.isFinite(mergedOptions.delay) ? mergedOptions.delay : DEFAULT_DELAY;
        const autohide = mergedOptions.autohide !== false;

        if (!messageText) {
            return;
        }

        if (!container || !window.bootstrap || !bootstrap.Toast) {
            window.alert(messageText);
            return;
        }

        const toastElement = document.createElement('div');
        toastElement.className = `toast app-toast app-toast-${variant}`;
        toastElement.setAttribute('role', variant === 'danger' || variant === 'warning' ? 'alert' : 'status');
        toastElement.setAttribute('aria-live', variant === 'danger' || variant === 'warning' ? 'assertive' : 'polite');
        toastElement.setAttribute('aria-atomic', 'true');
        toastElement.innerHTML = `
            <div class="d-flex">
                <div class="toast-body"></div>
                <button type="button" class="btn-close me-2 m-auto" data-bs-dismiss="toast" aria-label="Fechar"></button>
            </div>
        `;
        toastElement.querySelector('.toast-body').textContent = messageText;
        container.appendChild(toastElement);

        const toastInstance = new bootstrap.Toast(toastElement, {
            delay,
            autohide
        });
        toastInstance.show();

        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        }, { once: true });
    };

    const confirm = (options = {}) => {
        const title = options.title || 'Confirmar ação';
        const message = String(options.message || 'Deseja continuar?');
        const confirmText = options.confirmText || 'Confirmar';
        const cancelText = options.cancelText || 'Cancelar';
        const variant = normalizeVariant(options.variant || 'danger');

        if (!confirmModalElement || !confirmModalTitle || !confirmModalMessage || !confirmAcceptButton || !confirmCancelButton || !window.bootstrap || !bootstrap.Modal) {
            return Promise.resolve(window.confirm(message));
        }

        confirmModalTitle.textContent = title;
        confirmModalMessage.textContent = message;
        confirmAcceptButton.textContent = confirmText;
        confirmCancelButton.textContent = cancelText;
        confirmAcceptButton.classList.remove('btn-primary', 'btn-success', 'btn-warning', 'btn-danger');
        confirmAcceptButton.classList.add(
            variant === 'success'
                ? 'btn-success'
                : variant === 'warning'
                    ? 'btn-warning'
                    : variant === 'info'
                        ? 'btn-primary'
                        : 'btn-danger'
        );

        const modalInstance = bootstrap.Modal.getOrCreateInstance(confirmModalElement);

        return new Promise((resolve) => {
            let resolved = false;

            const cleanup = () => {
                confirmModalElement.removeEventListener('hidden.bs.modal', onHidden);
                confirmAcceptButton.removeEventListener('click', onConfirmClick);
                confirmCancelButton.removeEventListener('click', onCancelClick);
            };

            const finish = (value) => {
                if (resolved) {
                    return;
                }
                resolved = true;
                cleanup();
                resolve(value);
            };

            const onHidden = () => finish(false);
            const onCancelClick = () => {
                finish(false);
                modalInstance.hide();
            };
            const onConfirmClick = () => {
                finish(true);
                modalInstance.hide();
            };

            confirmModalElement.addEventListener('hidden.bs.modal', onHidden);
            confirmAcceptButton.addEventListener('click', onConfirmClick);
            confirmCancelButton.addEventListener('click', onCancelClick);

            modalInstance.show();
        });
    };

    const showDjangoMessagesFromDom = () => {
        const nodes = document.querySelectorAll('#django-messages .django-message');
        nodes.forEach((node) => {
            const text = node.textContent || '';
            const level = node.getAttribute('data-level') || '';
            showToast(text, { variant: normalizeVariant(level) });
        });
    };

    window.AppFeedback = {
        showToast,
        confirm,
        showDjangoMessagesFromDom
    };

    document.addEventListener('DOMContentLoaded', showDjangoMessagesFromDom);
}());
