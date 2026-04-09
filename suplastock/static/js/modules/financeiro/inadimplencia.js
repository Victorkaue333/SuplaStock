document.addEventListener('DOMContentLoaded', () => {
    const dataElement = document.getElementById('inadimplencia-kpi-data');
    const modalElement = document.getElementById('inadKpiModal');
    const modalTitle = document.getElementById('inadKpiModalTitle');
    const modalContent = document.getElementById('inadKpiModalContent');
    const kpiCards = document.querySelectorAll('.inad-kpi[data-kpi]');

    if (!dataElement || !modalElement || !modalTitle || !modalContent || !kpiCards.length || typeof bootstrap === 'undefined') {
        return;
    }

    let payload;
    try {
        payload = JSON.parse(dataElement.textContent);
    } catch (error) {
        console.error('Falha ao ler dados dos modais de KPI da inadimplência:', error);
        return;
    }

    const formatCurrency = (window.VAFormatters && typeof window.VAFormatters.formatCurrencyBRL === 'function')
        ? window.VAFormatters.formatCurrencyBRL
        : (value) => `R$ ${Number(value || 0).toFixed(2).replace('.', ',')}`;

    const formatNumber = (value) => new Intl.NumberFormat('pt-BR').format(Number(value || 0));
    const formatDecimal = (value, fractionDigits = 1) => Number(value || 0).toLocaleString(
        'pt-BR',
        {
            minimumFractionDigits: fractionDigits,
            maximumFractionDigits: fractionDigits,
        },
    );

    const escapeHtml = (value) => String(value ?? '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');

    const modal = new bootstrap.Modal(modalElement);
    const resumo = payload.resumo || {};
    const clientes = Array.isArray(payload.clientes) ? payload.clientes : [];
    const rankingDivida = Array.isArray(payload.ranking_divida) ? payload.ranking_divida : [];
    const rankingAtraso = Array.isArray(payload.ranking_atraso) ? payload.ranking_atraso : [];

    const summaryItem = (label, value) => `
        <article class="inad-kpi-summary-item">
            <span>${escapeHtml(label)}</span>
            <strong>${escapeHtml(value)}</strong>
        </article>
    `;

    const renderSection = ({ title, headers, rows, emptyMessage }) => {
        if (!rows.length) {
            return `
                <section class="inad-kpi-modal-section">
                    <h6>${escapeHtml(title)}</h6>
                    <p class="inad-kpi-modal-empty">${escapeHtml(emptyMessage || 'Sem dados disponíveis.')}</p>
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
            <section class="inad-kpi-modal-section">
                <h6>${escapeHtml(title)}</h6>
                <div class="inad-kpi-modal-table-wrap">
                    <table class="inad-kpi-modal-table">
                        <thead><tr>${head}</tr></thead>
                        <tbody>${body}</tbody>
                    </table>
                </div>
            </section>
        `;
    };

    const sortByName = (items) => [...items].sort((a, b) => {
        const nomeA = (a.cliente_nome || '').toLowerCase();
        const nomeB = (b.cliente_nome || '').toLowerCase();
        if (nomeA < nomeB) {
            return -1;
        }
        if (nomeA > nomeB) {
            return 1;
        }
        return Number(a.cliente_id || 0) - Number(b.cliente_id || 0);
    });

    const riskBadge = (item) => `<span class="risk-badge risk-${escapeHtml(item.risco_codigo || '')}">${escapeHtml(item.risco_label || '-')}</span>`;

    const mapClientRows = (items) => items.map((item) => ([
        { value: `${escapeHtml(item.cliente_nome)}${item.cliente_codigo ? ` <small>#${escapeHtml(item.cliente_codigo)}</small>` : ''}` },
        { value: formatCurrency(item.valor_em_atraso), className: 'inad-kpi-modal-number' },
        { value: formatNumber(item.contas_em_atraso), className: 'inad-kpi-modal-center' },
        { value: formatNumber(item.dias_em_atraso), className: 'inad-kpi-modal-center' },
        { value: escapeHtml(item.vencimento_antigo_label || '-'), className: 'inad-kpi-modal-center' },
        { value: escapeHtml(item.ultima_compra_label || '-'), className: 'inad-kpi-modal-center' },
        { value: escapeHtml(item.ultimo_pagamento_label || '-'), className: 'inad-kpi-modal-center' },
        { value: riskBadge(item), className: 'inad-kpi-modal-center' },
    ]));

    const mapRankingDividaRows = (items) => items.map((item, index) => ([
        { value: formatNumber(index + 1), className: 'inad-kpi-modal-center' },
        { value: `${escapeHtml(item.cliente_nome)}${item.cliente_codigo ? ` <small>#${escapeHtml(item.cliente_codigo)}</small>` : ''}` },
        { value: formatCurrency(item.valor_em_atraso), className: 'inad-kpi-modal-number' },
        { value: formatNumber(item.contas_em_atraso), className: 'inad-kpi-modal-center' },
        { value: formatNumber(item.dias_em_atraso), className: 'inad-kpi-modal-center' },
        { value: riskBadge(item), className: 'inad-kpi-modal-center' },
    ]));

    const mapRankingAtrasoRows = (items) => items.map((item, index) => ([
        { value: formatNumber(index + 1), className: 'inad-kpi-modal-center' },
        { value: `${escapeHtml(item.cliente_nome)}${item.cliente_codigo ? ` <small>#${escapeHtml(item.cliente_codigo)}</small>` : ''}` },
        { value: formatNumber(item.dias_em_atraso), className: 'inad-kpi-modal-center' },
        { value: formatCurrency(item.valor_em_atraso), className: 'inad-kpi-modal-number' },
        { value: formatNumber(item.contas_em_atraso), className: 'inad-kpi-modal-center' },
        { value: riskBadge(item), className: 'inad-kpi-modal-center' },
    ]));

    const buildTotalAtrasoModal = () => `
        <p class="inad-kpi-modal-intro">Referência: ${escapeHtml(resumo.hoje_label || '-')} ${resumo.filtro_cliente ? `| Filtro de cliente: "${escapeHtml(resumo.filtro_cliente)}"` : ''}</p>
        <div class="inad-kpi-modal-summary">
            ${summaryItem('Total em atraso', formatCurrency(resumo.total_em_atraso))}
            ${summaryItem('Clientes inadimplentes', formatNumber(resumo.quantidade_clientes))}
            ${summaryItem('Contas em atraso', formatNumber(resumo.total_contas_em_atraso))}
            ${summaryItem('Maior dívida', formatCurrency(resumo.maior_divida))}
        </div>
        ${renderSection({
            title: 'Ranking de maiores dívidas',
            headers: [
                { label: '#' }, { label: 'Cliente' }, { label: 'Valor em atraso' },
                { label: 'Contas' }, { label: 'Dias' }, { label: 'Risco' },
            ],
            rows: mapRankingDividaRows(rankingDivida),
            emptyMessage: 'Sem clientes inadimplentes.',
        })}
        ${renderSection({
            title: 'Base completa de clientes inadimplentes',
            headers: [
                { label: 'Cliente' }, { label: 'Valor em atraso' }, { label: 'Contas' }, { label: 'Dias' },
                { label: 'Venc. mais antigo' }, { label: 'Última compra' }, { label: 'Último pagamento' }, { label: 'Risco' },
            ],
            rows: mapClientRows(sortByName(clientes)),
            emptyMessage: 'Sem clientes inadimplentes.',
        })}
    `;

    const buildQuantidadeClientesModal = () => {
        const risco = resumo.risco_counts || {};
        return `
            <p class="inad-kpi-modal-intro">Referência: ${escapeHtml(resumo.hoje_label || '-')} ${resumo.filtro_cliente ? `| Filtro de cliente: "${escapeHtml(resumo.filtro_cliente)}"` : ''}</p>
            <div class="inad-kpi-modal-summary">
                ${summaryItem('Clientes inadimplentes', formatNumber(resumo.quantidade_clientes))}
                ${summaryItem('Com último pagamento', formatNumber(resumo.clientes_com_pagamento))}
                ${summaryItem('Sem registro de pagamento', formatNumber(resumo.clientes_sem_pagamento))}
                ${summaryItem('Contas em atraso', formatNumber(resumo.total_contas_em_atraso))}
                ${summaryItem('Risco leve', formatNumber(risco.leve || 0))}
                ${summaryItem('Risco médio', formatNumber(risco.medio || 0))}
                ${summaryItem('Risco grave', formatNumber(risco.grave || 0))}
            </div>
            ${renderSection({
                title: 'Clientes inadimplentes (base completa)',
                headers: [
                    { label: 'Cliente' }, { label: 'Valor em atraso' }, { label: 'Contas' }, { label: 'Dias' },
                    { label: 'Venc. mais antigo' }, { label: 'Última compra' }, { label: 'Último pagamento' }, { label: 'Risco' },
                ],
                rows: mapClientRows(sortByName(clientes)),
                emptyMessage: 'Sem clientes inadimplentes.',
            })}
        `;
    };

    const buildMediaDiasModal = () => `
        <p class="inad-kpi-modal-intro">Referência: ${escapeHtml(resumo.hoje_label || '-')} ${resumo.filtro_cliente ? `| Filtro de cliente: "${escapeHtml(resumo.filtro_cliente)}"` : ''}</p>
        <div class="inad-kpi-modal-summary">
            ${summaryItem('Média de dias em atraso', formatDecimal(resumo.media_dias_atraso))}
            ${summaryItem('Maior atraso', `${formatNumber(resumo.maior_atraso)} dia(s)`)}
            ${summaryItem('Menor atraso', `${formatNumber(resumo.menor_atraso)} dia(s)`)}
            ${summaryItem('Clientes analisados', formatNumber(resumo.quantidade_clientes))}
        </div>
        ${renderSection({
            title: 'Ranking de maior atraso',
            headers: [
                { label: '#' }, { label: 'Cliente' }, { label: 'Dias em atraso' },
                { label: 'Valor em atraso' }, { label: 'Contas' }, { label: 'Risco' },
            ],
            rows: mapRankingAtrasoRows(rankingAtraso),
            emptyMessage: 'Sem clientes com atraso.',
        })}
            ${renderSection({
                title: 'Base completa por dias de atraso',
                headers: [
                    { label: 'Cliente' }, { label: 'Dias' }, { label: 'Valor em atraso' }, { label: 'Contas' },
                    { label: 'Venc. mais antigo' }, { label: 'Último pagamento' }, { label: 'Risco' },
                ],
                rows: rankingAtraso.map((item) => ([
                    { value: `${escapeHtml(item.cliente_nome)}${item.cliente_codigo ? ` <small>#${escapeHtml(item.cliente_codigo)}</small>` : ''}` },
                    { value: formatNumber(item.dias_em_atraso), className: 'inad-kpi-modal-center' },
                    { value: formatCurrency(item.valor_em_atraso), className: 'inad-kpi-modal-number' },
                    { value: formatNumber(item.contas_em_atraso), className: 'inad-kpi-modal-center' },
                    { value: escapeHtml(item.vencimento_antigo_label || '-'), className: 'inad-kpi-modal-center' },
                    { value: escapeHtml(item.ultimo_pagamento_label || '-'), className: 'inad-kpi-modal-center' },
                    { value: riskBadge(item), className: 'inad-kpi-modal-center' },
                ])),
                emptyMessage: 'Sem clientes com atraso.',
            })}
        `;

    const buildMaiorDividaModal = () => {
        const maiorDividaCliente = resumo.maior_divida_cliente || null;
        return `
            <p class="inad-kpi-modal-intro">Referência: ${escapeHtml(resumo.hoje_label || '-')} ${resumo.filtro_cliente ? `| Filtro de cliente: "${escapeHtml(resumo.filtro_cliente)}"` : ''}</p>
            <div class="inad-kpi-modal-summary">
                ${summaryItem('Maior dívida', formatCurrency(resumo.maior_divida))}
                ${summaryItem('Cliente da maior dívida', maiorDividaCliente ? maiorDividaCliente.cliente_nome : '-')}
                ${summaryItem('Dias de atraso (maior dívida)', maiorDividaCliente ? `${formatNumber(maiorDividaCliente.dias_em_atraso)} dia(s)` : '-')}
                ${summaryItem('Contas em atraso (maior dívida)', maiorDividaCliente ? formatNumber(maiorDividaCliente.contas_em_atraso) : '-')}
            </div>
            ${renderSection({
                title: 'Ranking completo por valor em atraso',
                headers: [
                    { label: '#' }, { label: 'Cliente' }, { label: 'Valor em atraso' },
                    { label: 'Contas' }, { label: 'Dias' }, { label: 'Risco' },
                ],
                rows: mapRankingDividaRows(rankingDivida),
                emptyMessage: 'Sem clientes inadimplentes.',
            })}
            ${renderSection({
                title: 'Base completa de clientes inadimplentes',
                headers: [
                    { label: 'Cliente' }, { label: 'Valor em atraso' }, { label: 'Contas' }, { label: 'Dias' },
                    { label: 'Venc. mais antigo' }, { label: 'Última compra' }, { label: 'Último pagamento' }, { label: 'Risco' },
                ],
                rows: mapClientRows(sortByName(clientes)),
                emptyMessage: 'Sem clientes inadimplentes.',
            })}
        `;
    };

    const modalBuilders = {
        total_em_atraso: { title: 'Total em Atraso', build: buildTotalAtrasoModal },
        quantidade_clientes: { title: 'Clientes Inadimplentes', build: buildQuantidadeClientesModal },
        media_dias_atraso: { title: 'Média de Dias em Atraso', build: buildMediaDiasModal },
        maior_divida: { title: 'Maior Dívida em Atraso', build: buildMaiorDividaModal },
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
