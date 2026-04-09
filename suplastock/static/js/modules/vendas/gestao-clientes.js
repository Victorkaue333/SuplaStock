const clientesDeleteConfigElement = document.getElementById('clientes-delete-config');
const clientesEditUrlTemplate = clientesDeleteConfigElement
    ? (clientesDeleteConfigElement.dataset.editUrlTemplate || '')
    : '';
const clientesDeleteUrlTemplate = clientesDeleteConfigElement
    ? (clientesDeleteConfigElement.dataset.deleteUrlTemplate || '')
    : '';
const clientesCsrfToken = clientesDeleteConfigElement
    ? (clientesDeleteConfigElement.dataset.csrfToken || '')
    : '';

function buildClienteUrl(urlTemplate, id) {
    if (urlTemplate.includes('/0/')) {
        return urlTemplate.replace('/0/', `/${id}/`);
    }
    return '';
}

function openModal(id) {
    document.getElementById(id).classList.add('active');
}

function closeModal(id) {
    document.getElementById(id).classList.remove('active');
}

const CLIENTE_FILTER_DEBOUNCE_MS = 320;
let clienteFilterTimer = null;

function filterTable() {
    const input = document.getElementById('searchCliente');
    const table = document.getElementById('tableClientes');
    if (!input || !table) {
        return;
    }

    const filter = input.value.toLowerCase().trim();
    const rows = table.getElementsByTagName('tr');

    for (let i = 1; i < rows.length; i++) {
        const cells = rows[i].getElementsByTagName('td');
        let match = false;

        for (let j = 0; j < cells.length - 1; j++) {
            if (cells[j].textContent.toLowerCase().includes(filter)) {
                match = true;
                break;
            }
        }

        rows[i].style.display = match ? '' : 'none';
    }
}

function toggleClienteSearchClear() {
    const input = document.getElementById('searchCliente');
    const clearButton = document.getElementById('clearClienteSearch');
    if (!input || !clearButton) {
        return;
    }

    clearButton.hidden = !input.value.trim();
}

function runClienteFilterNow() {
    if (clienteFilterTimer) {
        clearTimeout(clienteFilterTimer);
        clienteFilterTimer = null;
    }
    filterTable();
    toggleClienteSearchClear();
}

function queueClienteFilter() {
    if (clienteFilterTimer) {
        clearTimeout(clienteFilterTimer);
    }
    clienteFilterTimer = setTimeout(runClienteFilterNow, CLIENTE_FILTER_DEBOUNCE_MS);
}

function clearClienteSearch() {
    const input = document.getElementById('searchCliente');
    if (!input) {
        return;
    }

    input.value = '';
    runClienteFilterNow();
    input.focus();
}

function editarCliente(id) {
    const editUrl = buildClienteUrl(clientesEditUrlTemplate, id);
    if (!editUrl) {
        window.AppFeedback?.showToast?.('Rota de edição de cliente não configurada.', { variant: 'danger' });
        return;
    }
    window.location.href = editUrl;
}

function deletarCliente(id, nome) {
    const confirmationText = `Tem certeza que deseja excluir o cliente "${nome}"?`;
    const confirmPromise = window.AppFeedback?.confirm
        ? window.AppFeedback.confirm({
            title: 'Excluir cliente',
            message: confirmationText,
            confirmText: 'Excluir',
            cancelText: 'Cancelar',
            variant: 'danger'
        })
        : Promise.resolve(window.confirm(confirmationText));

    confirmPromise.then((confirmed) => {
        if (!confirmed) {
            return;
        }

        const form = document.createElement('form');
        form.method = 'POST';
        form.action = buildClienteUrl(clientesDeleteUrlTemplate, id);
        if (!form.action) {
            window.AppFeedback?.showToast?.('Rota de exclusão de cliente não configurada.', { variant: 'danger' });
            return;
        }

        const csrfInput = document.createElement('input');
        csrfInput.type = 'hidden';
        csrfInput.name = 'csrfmiddlewaretoken';
        csrfInput.value = clientesCsrfToken || (document.querySelector('[name=csrfmiddlewaretoken]')?.value || '');
        form.appendChild(csrfInput);

        document.body.appendChild(form);
        form.submit();
    });
}

document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('searchCliente');
    const clearButton = document.getElementById('clearClienteSearch');

    if (input) {
        input.addEventListener('input', queueClienteFilter);
        input.addEventListener('keydown', (event) => {
            if (event.key !== 'Enter') {
                return;
            }
            event.preventDefault();
            runClienteFilterNow();
        });
        toggleClienteSearchClear();
    }

    if (clearButton) {
        clearButton.addEventListener('click', clearClienteSearch);
    }
});

// Close modal when clicking outside
window.addEventListener('click', (event) => {
    if (event.target.classList.contains('modal')) {
        event.target.classList.remove('active');
    }
});
