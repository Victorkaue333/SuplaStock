document.addEventListener('DOMContentLoaded', () => {
    const dataElement = document.getElementById('alertas-kpi-data');
    const modalElement = document.getElementById('alertasKpiModal');
    const modalTitle = document.getElementById('alertasKpiModalTitle');
    const modalContent = document.getElementById('alertasKpiModalContent');
    const kpiCards = document.querySelectorAll('.alerta-kpi[data-kpi]');

    if (!dataElement || !modalElement || !modalTitle || !modalContent || !kpiCards.length || typeof bootstrap === 'undefined') {
        return;
    }

    let payload;
    try {
        payload = JSON.parse(dataElement.textContent);
    } catch (error) {
        console.error('Falha ao ler dados dos modais de KPI dos alertas:', error);
        return;
    }

    const formatCurrency = (window.VAFormatters && typeof window.VAFormatters.formatCurrencyBRL === 'function')
        ? window.VAFormatters.formatCurrencyBRL
        : (value) => `R$ ${Number(value || 0).toFixed(2).replace('.', ',')}`;

    const formatNumber = (value) => new Intl.NumberFormat('pt-BR').format(Number(value || 0));

    const escapeHtml = (value) => String(value ?? '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');

    const modal = new bootstrap.Modal(modalElement);
    const resumo = payload.resumo || {};
    const contasVencendoHoje = Array.isArray(payload.contas_vencendo_hoje) ? payload.contas_vencendo_hoje : [];
    const contasAtrasadas = Array.isArray(payload.contas_atrasadas) ? payload.contas_atrasadas : [];
    const estoqueBaixo = Array.isArray(payload.estoque_baixo) ? payload.estoque_baixo : [];
    const produtosSemEstoque = Array.isArray(payload.produtos_sem_estoque) ? payload.produtos_sem_estoque : [];
    const contasPagarVencendoHoje = Array.isArray(payload.contas_pagar_vencendo_hoje) ? payload.contas_pagar_vencendo_hoje : [];
    const contasPagarAtrasadas = Array.isArray(payload.contas_pagar_atrasadas) ? payload.contas_pagar_atrasadas : [];

    const summaryItem = (label, value) => `
        <article class="alertas-kpi-summary-item">
            <span>${escapeHtml(label)}</span>
            <strong>${escapeHtml(value)}</strong>
        </article>
    `;

    const renderSection = ({ title, headers, rows, emptyMessage }) => {
        if (!rows.length) {
            return `
                <section class="alertas-kpi-modal-section">
                    <h6>${escapeHtml(title)}</h6>
                    <p class="alertas-kpi-modal-empty">${escapeHtml(emptyMessage || 'Sem dados disponíveis.')}</p>
                </section>
            `;
        }

        const head = headers
            .map((header) => `<th class="${header.className || ''}">${escapeHtml(header.label)}</th>`)
            .join('');

        const body = rows
            .map((row) => `
                <tr>
                    ${row.map((cell) => `<td class="${cell.className || ''}">${cell.value}</td>`).join('')}
                </tr>
            `)
            .join('');

        return `
            <section class="alertas-kpi-modal-section">
                <h6>${escapeHtml(title)}</h6>
                <div class="alertas-kpi-modal-table-wrap">
                    <table class="alertas-kpi-modal-table">
                        <thead><tr>${head}</tr></thead>
                        <tbody>${body}</tbody>
                    </table>
                </div>
            </section>
        `;
    };

    const contasVencendoRows = contasVencendoHoje.map((item) => ([
        { value: escapeHtml(item.cliente_nome || '-') },
        { value: escapeHtml(item.descricao || '-') },
        { value: formatCurrency(item.valor), className: 'alertas-kpi-modal-number' },
        { value: escapeHtml(item.vencimento_label || '-'), className: 'alertas-kpi-modal-center' },
    ]));

    const contasAtrasadasRows = contasAtrasadas.map((item) => ([
        { value: escapeHtml(item.cliente_nome || '-') },
        { value: escapeHtml(item.descricao || '-') },
        { value: formatCurrency(item.valor), className: 'alertas-kpi-modal-number' },
        { value: formatNumber(item.dias_atraso), className: 'alertas-kpi-modal-center' },
        { value: escapeHtml(item.vencimento_label || '-'), className: 'alertas-kpi-modal-center' },
    ]));

    const estoqueBaixoRows = estoqueBaixo.map((item) => ([
        { value: escapeHtml(item.produto_nome || '-') },
        { value: escapeHtml(item.categoria || '-') },
        { value: escapeHtml(item.fornecedor || '-') },
        { value: formatNumber(item.estoque_atual), className: 'alertas-kpi-modal-center' },
        { value: formatNumber(item.estoque_minimo), className: 'alertas-kpi-modal-center' },
        { value: formatNumber(item.falta_para_minimo), className: 'alertas-kpi-modal-center' },
        { value: escapeHtml(item.data_validade_label || '-'), className: 'alertas-kpi-modal-center' },
    ]));

    const produtosSemEstoqueRows = produtosSemEstoque.map((item) => ([
        { value: escapeHtml(item.produto_nome || '-') },
        { value: escapeHtml(item.categoria || '-') },
        { value: escapeHtml(item.fornecedor || '-') },
        { value: formatNumber(item.estoque_atual), className: 'alertas-kpi-modal-center' },
        { value: formatNumber(item.estoque_minimo), className: 'alertas-kpi-modal-center' },
        { value: escapeHtml(item.data_validade_label || '-'), className: 'alertas-kpi-modal-center' },
    ]));

    const contasPagarHojeRows = contasPagarVencendoHoje.map((item) => ([
        { value: escapeHtml(item.descricao || '-') },
        { value: escapeHtml(item.categoria || '-') },
        { value: escapeHtml(item.fornecedor || '-') },
        { value: formatCurrency(item.valor), className: 'alertas-kpi-modal-number' },
        { value: escapeHtml(item.vencimento_label || '-'), className: 'alertas-kpi-modal-center' },
    ]));

    const contasPagarAtrasadasRows = contasPagarAtrasadas.map((item) => ([
        { value: escapeHtml(item.descricao || '-') },
        { value: escapeHtml(item.categoria || '-') },
        { value: formatCurrency(item.valor), className: 'alertas-kpi-modal-number' },
        { value: formatNumber(item.dias_atraso), className: 'alertas-kpi-modal-center' },
        { value: escapeHtml(item.vencimento_label || '-'), className: 'alertas-kpi-modal-center' },
    ]));

    const buildTotalAlertasModal = () => `
        <p class="alertas-kpi-modal-intro">Referência: ${escapeHtml(resumo.hoje_label || '-')}</p>
        <div class="alertas-kpi-modal-summary">
            ${summaryItem('Total de alertas', formatNumber(resumo.total_alertas))}
            ${summaryItem('Alertas críticos', formatNumber(resumo.alertas_criticos))}
            ${summaryItem('Ações para hoje', formatNumber(resumo.alertas_hoje))}
            ${summaryItem('Alertas de estoque', formatNumber(resumo.total_alertas_estoque))}
            ${summaryItem('Contas atrasadas', formatNumber(resumo.contas_atrasadas_count))}
            ${summaryItem('Sem estoque', formatNumber(resumo.produtos_sem_estoque_count))}
        </div>
        ${renderSection({
            title: 'Contas vencendo hoje',
            headers: [{ label: 'Cliente' }, { label: 'Descrição' }, { label: 'Valor' }, { label: 'Vencimento' }],
            rows: contasVencendoRows,
            emptyMessage: 'Sem contas vencendo hoje.',
        })}
        ${renderSection({
            title: 'Contas atrasadas',
            headers: [{ label: 'Cliente' }, { label: 'Descrição' }, { label: 'Valor' }, { label: 'Dias atraso' }, { label: 'Vencimento' }],
            rows: contasAtrasadasRows,
            emptyMessage: 'Sem contas atrasadas.',
        })}
        ${renderSection({
            title: 'Estoque baixo',
            headers: [{ label: 'Produto' }, { label: 'Categoria' }, { label: 'Fornecedor' }, { label: 'Estoque' }, { label: 'Mínimo' }, { label: 'Falta' }, { label: 'Validade' }],
            rows: estoqueBaixoRows,
            emptyMessage: 'Sem produtos com estoque baixo.',
        })}
        ${renderSection({
            title: 'Produtos sem estoque',
            headers: [{ label: 'Produto' }, { label: 'Categoria' }, { label: 'Fornecedor' }, { label: 'Estoque' }, { label: 'Mínimo' }, { label: 'Validade' }],
            rows: produtosSemEstoqueRows,
            emptyMessage: 'Sem produtos zerados.',
        })}
        ${renderSection({
            title: 'Contas a pagar vencendo hoje',
            headers: [{ label: 'Descrição' }, { label: 'Categoria' }, { label: 'Fornecedor' }, { label: 'Valor' }, { label: 'Vencimento' }],
            rows: contasPagarHojeRows,
            emptyMessage: 'Sem contas a pagar vencendo hoje.',
        })}
        ${renderSection({
            title: 'Contas a pagar atrasadas',
            headers: [{ label: 'Descrição' }, { label: 'Categoria' }, { label: 'Valor' }, { label: 'Dias atraso' }, { label: 'Vencimento' }],
            rows: contasPagarAtrasadasRows,
            emptyMessage: 'Sem contas a pagar atrasadas.',
        })}
    `;

    const buildAlertasCriticosModal = () => `
        <p class="alertas-kpi-modal-intro">Referência: ${escapeHtml(resumo.hoje_label || '-')}</p>
        <div class="alertas-kpi-modal-summary">
            ${summaryItem('Alertas críticos', formatNumber(resumo.alertas_criticos))}
            ${summaryItem('Contas atrasadas', formatNumber(resumo.contas_atrasadas_count))}
            ${summaryItem('Produtos sem estoque', formatNumber(resumo.produtos_sem_estoque_count))}
            ${summaryItem('Contas a pagar atrasadas', formatNumber(resumo.contas_pagar_atrasadas_count))}
        </div>
        ${renderSection({
            title: 'Contas atrasadas (receber)',
            headers: [{ label: 'Cliente' }, { label: 'Descrição' }, { label: 'Valor' }, { label: 'Dias atraso' }, { label: 'Vencimento' }],
            rows: contasAtrasadasRows,
            emptyMessage: 'Sem contas atrasadas.',
        })}
        ${renderSection({
            title: 'Produtos sem estoque',
            headers: [{ label: 'Produto' }, { label: 'Categoria' }, { label: 'Fornecedor' }, { label: 'Estoque' }, { label: 'Mínimo' }, { label: 'Validade' }],
            rows: produtosSemEstoqueRows,
            emptyMessage: 'Sem produtos sem estoque.',
        })}
        ${renderSection({
            title: 'Contas a pagar atrasadas',
            headers: [{ label: 'Descrição' }, { label: 'Categoria' }, { label: 'Valor' }, { label: 'Dias atraso' }, { label: 'Vencimento' }],
            rows: contasPagarAtrasadasRows,
            emptyMessage: 'Sem contas a pagar atrasadas.',
        })}
    `;

    const buildAcoesHojeModal = () => `
        <p class="alertas-kpi-modal-intro">Referência: ${escapeHtml(resumo.hoje_label || '-')}</p>
        <div class="alertas-kpi-modal-summary">
            ${summaryItem('Ações para hoje', formatNumber(resumo.alertas_hoje))}
            ${summaryItem('Contas vencendo hoje', formatNumber(resumo.contas_vencendo_hoje_count))}
            ${summaryItem('Contas a pagar hoje', formatNumber(resumo.contas_pagar_vencendo_hoje_count))}
        </div>
        ${renderSection({
            title: 'Contas a receber vencendo hoje',
            headers: [{ label: 'Cliente' }, { label: 'Descrição' }, { label: 'Valor' }, { label: 'Vencimento' }],
            rows: contasVencendoRows,
            emptyMessage: 'Sem contas a receber vencendo hoje.',
        })}
        ${renderSection({
            title: 'Contas a pagar vencendo hoje',
            headers: [{ label: 'Descrição' }, { label: 'Categoria' }, { label: 'Fornecedor' }, { label: 'Valor' }, { label: 'Vencimento' }],
            rows: contasPagarHojeRows,
            emptyMessage: 'Sem contas a pagar vencendo hoje.',
        })}
    `;

    const buildAlertasEstoqueModal = () => `
        <p class="alertas-kpi-modal-intro">Referência: ${escapeHtml(resumo.hoje_label || '-')}</p>
        <div class="alertas-kpi-modal-summary">
            ${summaryItem('Alertas de estoque', formatNumber(resumo.total_alertas_estoque))}
            ${summaryItem('Estoque baixo', formatNumber(resumo.estoque_baixo_count))}
            ${summaryItem('Produtos sem estoque', formatNumber(resumo.produtos_sem_estoque_count))}
        </div>
        ${renderSection({
            title: 'Produtos com estoque baixo',
            headers: [{ label: 'Produto' }, { label: 'Categoria' }, { label: 'Fornecedor' }, { label: 'Estoque' }, { label: 'Mínimo' }, { label: 'Falta' }, { label: 'Validade' }],
            rows: estoqueBaixoRows,
            emptyMessage: 'Sem produtos com estoque baixo.',
        })}
        ${renderSection({
            title: 'Produtos sem estoque',
            headers: [{ label: 'Produto' }, { label: 'Categoria' }, { label: 'Fornecedor' }, { label: 'Estoque' }, { label: 'Mínimo' }, { label: 'Validade' }],
            rows: produtosSemEstoqueRows,
            emptyMessage: 'Sem produtos sem estoque.',
        })}
    `;

    const modalBuilders = {
        total_alertas: { title: 'Total de Alertas', build: buildTotalAlertasModal },
        alertas_criticos: { title: 'Alertas Críticos', build: buildAlertasCriticosModal },
        alertas_hoje: { title: 'Ações para Hoje', build: buildAcoesHojeModal },
        total_alertas_estoque: { title: 'Alertas de Estoque', build: buildAlertasEstoqueModal },
    };

    const openKpiModal = (kpiKey) => {
        const config = modalBuilders[kpiKey];
        if (!config) {
            return;
        }
        modalTitle.textContent = config.title;
        modalContent.innerHTML = config.build();
        modal.show();
    };

    kpiCards.forEach((card) => {
        card.addEventListener('click', () => openKpiModal(card.dataset.kpi));
        card.addEventListener('keydown', (event) => {
            if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                openKpiModal(card.dataset.kpi);
            }
        });
    });
});
