document.addEventListener('DOMContentLoaded', () => {
    const chartDataElement = document.getElementById('relatorios-gerenciais-chart-data');
    const chartVendasCanvas = document.getElementById('chartRelatoriosVendas');
    const chartLucroCanvas = document.getElementById('chartRelatoriosLucro');

    const formatCurrency = (window.VAFormatters && typeof window.VAFormatters.formatCurrencyBRL === 'function')
        ? window.VAFormatters.formatCurrencyBRL
        : (value) => `R$ ${Number(value || 0).toFixed(2).replace('.', ',')}`;

    const formatNumber = (value) => new Intl.NumberFormat('pt-BR').format(Number(value || 0));
    const formatCurrencyCompact = (value) => {
        const amount = Number(value || 0);
        const abs = Math.abs(amount);
        const signal = amount < 0 ? '-' : '';
        if (abs >= 1000000) {
            return `${signal}R$ ${(abs / 1000000).toFixed(1).replace('.', ',')} mi`;
        }
        if (abs >= 1000) {
            return `${signal}R$ ${(abs / 1000).toFixed(0)} mil`;
        }
        return `${signal}R$ ${abs.toFixed(0).replace('.', ',')}`;
    };
    const calculateBounds = (values, { includeZero = false, paddingRatio = 0.1 } = {}) => {
        if (!Array.isArray(values) || !values.length) {
            return { min: 0, max: 0, padding: 0 };
        }
        const numeric = values.map((value) => Number(value || 0));
        let min = Math.min(...numeric);
        let max = Math.max(...numeric);
        if (includeZero) {
            min = Math.min(min, 0);
            max = Math.max(max, 0);
        }
        const span = Math.abs(max - min);
        const padding = span > 0 ? span * paddingRatio : Math.max(Math.abs(max) * paddingRatio, 1);
        return { min, max, padding };
    };

    if (chartDataElement && (chartVendasCanvas || chartLucroCanvas) && typeof Chart !== 'undefined') {
        let chartPayload;
        try {
            chartPayload = JSON.parse(chartDataElement.textContent);
        } catch (error) {
            console.error('Falha ao ler dados do gráfico de relatórios:', error);
            chartPayload = null;
        }

        if (chartPayload) {
            const labels = chartPayload.labels || [];
            const vendas = chartPayload.vendas || [];
            const lucros = chartPayload.lucros || [];
            const margens = chartPayload.margens || [];
            const quantidades = chartPayload.quantidades || [];

            if (chartVendasCanvas) {
                new Chart(chartVendasCanvas.getContext('2d'), {
                    type: 'bar',
                    data: {
                        labels,
                        datasets: [
                            {
                                label: 'Vendas',
                                data: vendas,
                                backgroundColor: 'rgba(37, 99, 235, 0.78)',
                                borderColor: 'rgba(29, 78, 216, 0.9)',
                                borderWidth: 1,
                                borderRadius: 8,
                                maxBarThickness: 44,
                                categoryPercentage: 0.68,
                                barPercentage: 0.9,
                            },
                        ],
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        interaction: {
                            mode: 'index',
                            intersect: false,
                        },
                        plugins: {
                            legend: {
                                display: false,
                            },
                            tooltip: {
                                callbacks: {
                                    label: (ctx) => `Vendas: ${formatCurrency(ctx.parsed.y)}`,
                                    afterLabel: (ctx) => {
                                        const qtd = Number(quantidades[ctx.dataIndex] || 0);
                                        return `Qtd. vendas: ${formatNumber(qtd)}`;
                                    },
                                },
                            },
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                ticks: {
                                    callback: (value) => formatCurrencyCompact(value),
                                    maxTicksLimit: 6,
                                },
                                grid: {
                                    color: 'rgba(148, 163, 184, 0.18)',
                                },
                            },
                            x: {
                                grid: {
                                    display: false,
                                },
                                ticks: {
                                    autoSkip: true,
                                    maxRotation: 0,
                                    maxTicksLimit: 10,
                                },
                            },
                        },
                    },
                });
            }

            if (chartLucroCanvas) {
                const lucroBounds = calculateBounds(lucros, { includeZero: true, paddingRatio: 0.12 });
                new Chart(chartLucroCanvas.getContext('2d'), {
                    type: 'line',
                    data: {
                        labels,
                        datasets: [
                            {
                                label: 'Lucro',
                                data: lucros,
                                borderColor: '#059669',
                                backgroundColor: 'rgba(5, 150, 105, 0.14)',
                                borderWidth: 2.5,
                                pointRadius: 3,
                                pointHoverRadius: 4,
                                fill: true,
                                tension: 0.25,
                            },
                        ],
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        interaction: {
                            mode: 'index',
                            intersect: false,
                        },
                        plugins: {
                            legend: {
                                display: false,
                            },
                            tooltip: {
                                callbacks: {
                                    label: (ctx) => `Lucro: ${formatCurrency(ctx.parsed.y)}`,
                                    afterLabel: (ctx) => {
                                        const margem = Number(margens[ctx.dataIndex] || 0);
                                        return `Margem: ${margem.toFixed(2).replace('.', ',')}%`;
                                    },
                                },
                            },
                        },
                        scales: {
                            y: {
                                beginAtZero: false,
                                suggestedMin: lucroBounds.min - lucroBounds.padding,
                                suggestedMax: lucroBounds.max + lucroBounds.padding,
                                ticks: {
                                    callback: (value) => formatCurrencyCompact(value),
                                    maxTicksLimit: 6,
                                },
                                grid: {
                                    color: 'rgba(148, 163, 184, 0.18)',
                                },
                            },
                            x: {
                                grid: {
                                    display: false,
                                },
                                ticks: {
                                    autoSkip: true,
                                    maxRotation: 0,
                                    maxTicksLimit: 10,
                                },
                            },
                        },
                    },
                });
            }
        }
    }

    const kpiDataElement = document.getElementById('relatorios-gerenciais-kpi-data');
    const modalElement = document.getElementById('relatoriosKpiModal');
    const modalTitle = document.getElementById('relatoriosKpiModalTitle');
    const modalContent = document.getElementById('relatoriosKpiModalContent');
    const kpiCards = document.querySelectorAll('.relatorio-kpi-card[data-kpi]');

    if (!kpiDataElement || !modalElement || !modalTitle || !modalContent || !kpiCards.length || typeof bootstrap === 'undefined') {
        return;
    }

    let kpiPayload;
    try {
        kpiPayload = JSON.parse(kpiDataElement.textContent);
    } catch (error) {
        console.error('Falha ao ler dados dos modais de KPI:', error);
        return;
    }

    const modal = new bootstrap.Modal(modalElement);
    const resumo = kpiPayload.resumo || {};
    const vendasPeriodo = kpiPayload.vendas_por_periodo || [];
    const produtosMaisVendidos = kpiPayload.produtos_mais_vendidos || [];
    const clientesMaisCompram = kpiPayload.clientes_mais_compram || [];
    const clientesInadimplentes = kpiPayload.clientes_inadimplentes || [];
    const tabelaClientes = kpiPayload.tabela_clientes || [];

    const escapeHtml = (value) => String(value ?? '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');

    const summaryItem = (label, value) => `
        <article class="kpi-summary-item">
            <span>${escapeHtml(label)}</span>
            <strong>${escapeHtml(value)}</strong>
        </article>
    `;

    const renderSection = ({ title, headers, rows, emptyMessage }) => {
        if (!rows.length) {
            return `
                <section class="kpi-modal-section">
                    <h6>${escapeHtml(title)}</h6>
                    <p class="kpi-modal-empty">${escapeHtml(emptyMessage || 'Sem dados disponíveis.')}</p>
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
            <section class="kpi-modal-section">
                <h6>${escapeHtml(title)}</h6>
                <div class="kpi-modal-table-wrap">
                    <table class="kpi-modal-table">
                        <thead><tr>${head}</tr></thead>
                        <tbody>${body}</tbody>
                    </table>
                </div>
            </section>
        `;
    };

    const buildTotalVendasModal = () => {
        const vendasRows = vendasPeriodo.map((item) => ([
            { value: escapeHtml(item.label) },
            { value: formatCurrency(item.receita), className: 'kpi-modal-number' },
            { value: formatNumber(item.quantidade), className: 'kpi-modal-number' },
            { value: formatCurrency(item.lucro), className: 'kpi-modal-number' },
        ]));

        const produtosRows = produtosMaisVendidos.map((item) => ([
            { value: escapeHtml(item.produto) },
            { value: formatNumber(item.quantidade), className: 'kpi-modal-number' },
            { value: formatCurrency(item.receita), className: 'kpi-modal-number' },
        ]));

        const clientesRows = clientesMaisCompram.map((item) => ([
            { value: `${escapeHtml(item.cliente_nome)}${item.cliente_codigo ? ` <small>#${escapeHtml(item.cliente_codigo)}</small>` : ''}` },
            { value: formatNumber(item.quantidade_vendas), className: 'kpi-modal-number' },
            { value: formatCurrency(item.total_comprado), className: 'kpi-modal-number' },
        ]));

        return `
            <p class="kpi-modal-intro">Período analisado: ${escapeHtml(resumo.periodo?.inicio || '-')} até ${escapeHtml(resumo.periodo?.fim || '-')}</p>
            <div class="kpi-modal-summary">
                ${summaryItem('Total de vendas', formatCurrency(resumo.total_vendas))}
                ${summaryItem('Quantidade de vendas', formatNumber(resumo.quantidade_vendas))}
                ${summaryItem('Ticket médio', formatCurrency(resumo.ticket_medio))}
            </div>
            ${renderSection({
                title: 'Vendas por período',
                headers: [
                    { label: 'Período' },
                    { label: 'Receita' },
                    { label: 'Qtd. vendas' },
                    { label: 'Lucro' },
                ],
                rows: vendasRows,
                emptyMessage: 'Sem vendas no período.',
            })}
            ${renderSection({
                title: 'Produtos mais vendidos',
                headers: [
                    { label: 'Produto' },
                    { label: 'Quantidade' },
                    { label: 'Receita' },
                ],
                rows: produtosRows,
                emptyMessage: 'Sem produtos vendidos.',
            })}
            ${renderSection({
                title: 'Clientes que mais compram',
                headers: [
                    { label: 'Cliente' },
                    { label: 'Compras' },
                    { label: 'Total comprado' },
                ],
                rows: clientesRows,
                emptyMessage: 'Sem clientes com compras no período.',
            })}
        `;
    };

    const buildTotalRecebidoModal = () => {
        const totalSaldoAberto = tabelaClientes.reduce((acc, item) => acc + Number(item.saldo_em_aberto || 0), 0);
        const clientesPagantes = [...tabelaClientes]
            .filter((item) => Number(item.total_pago || 0) > 0)
            .sort((a, b) => Number(b.total_pago || 0) - Number(a.total_pago || 0));

        const pagantesRows = clientesPagantes.map((item) => ([
            { value: `${escapeHtml(item.cliente_nome)}${item.cliente_codigo ? ` <small>#${escapeHtml(item.cliente_codigo)}</small>` : ''}` },
            { value: formatCurrency(item.total_pago), className: 'kpi-modal-number' },
            { value: formatCurrency(item.saldo_em_aberto), className: 'kpi-modal-number' },
        ]));

        const inadRows = clientesInadimplentes.map((item) => ([
            { value: `${escapeHtml(item.cliente_nome)}${item.cliente_codigo ? ` <small>#${escapeHtml(item.cliente_codigo)}</small>` : ''}` },
            { value: formatCurrency(item.valor_em_aberto), className: 'kpi-modal-number' },
            { value: `${formatNumber(item.dias_atraso)} dia(s)`, className: 'kpi-modal-number' },
            { value: formatNumber(item.contas_em_atraso), className: 'kpi-modal-number' },
        ]));

        return `
            <p class="kpi-modal-intro">Período analisado: ${escapeHtml(resumo.periodo?.inicio || '-')} até ${escapeHtml(resumo.periodo?.fim || '-')}</p>
            <div class="kpi-modal-summary">
                ${summaryItem('Total recebido', formatCurrency(resumo.total_recebido))}
                ${summaryItem('Clientes com pagamento', formatNumber(clientesPagantes.length))}
                ${summaryItem('Saldo em aberto (base clientes)', formatCurrency(totalSaldoAberto))}
            </div>
            ${renderSection({
                title: 'Clientes com recebimentos no período',
                headers: [
                    { label: 'Cliente' },
                    { label: 'Total pago' },
                    { label: 'Saldo em aberto' },
                ],
                rows: pagantesRows,
                emptyMessage: 'Nenhum pagamento registrado no período.',
            })}
            ${renderSection({
                title: 'Clientes inadimplentes relacionados',
                headers: [
                    { label: 'Cliente' },
                    { label: 'Valor em aberto' },
                    { label: 'Dias de atraso' },
                    { label: 'Contas em atraso' },
                ],
                rows: inadRows,
                emptyMessage: 'Sem inadimplência vinculada.',
            })}
        `;
    };

    const buildLucroModal = () => {
        const margem = Number(resumo.total_vendas || 0) > 0
            ? (Number(resumo.lucro_estimado || 0) / Number(resumo.total_vendas || 1)) * 100
            : 0;

        const lucroRows = vendasPeriodo.map((item) => {
            const margemPeriodo = Number(item.receita || 0) > 0
                ? (Number(item.lucro || 0) / Number(item.receita || 1)) * 100
                : 0;
            return [
                { value: escapeHtml(item.label) },
                { value: formatCurrency(item.receita), className: 'kpi-modal-number' },
                { value: formatCurrency(item.lucro), className: 'kpi-modal-number' },
                { value: `${margemPeriodo.toFixed(2).replace('.', ',')}%`, className: 'kpi-modal-number' },
            ];
        });

        const clientesRows = clientesMaisCompram.map((item) => ([
            { value: `${escapeHtml(item.cliente_nome)}${item.cliente_codigo ? ` <small>#${escapeHtml(item.cliente_codigo)}</small>` : ''}` },
            { value: formatCurrency(item.total_comprado), className: 'kpi-modal-number' },
            { value: formatCurrency(item.ticket_medio), className: 'kpi-modal-number' },
        ]));

        return `
            <p class="kpi-modal-intro">Período analisado: ${escapeHtml(resumo.periodo?.inicio || '-')} até ${escapeHtml(resumo.periodo?.fim || '-')}</p>
            <div class="kpi-modal-summary">
                ${summaryItem('Lucro estimado', formatCurrency(resumo.lucro_estimado))}
                ${summaryItem('Margem estimada', `${margem.toFixed(2).replace('.', ',')}%`)}
                ${summaryItem('Total de vendas', formatCurrency(resumo.total_vendas))}
            </div>
            ${renderSection({
                title: 'Lucro por período',
                headers: [
                    { label: 'Período' },
                    { label: 'Receita' },
                    { label: 'Lucro' },
                    { label: 'Margem' },
                ],
                rows: lucroRows,
                emptyMessage: 'Sem lucro apurado no período.',
            })}
            ${renderSection({
                title: 'Clientes com maior volume (referência)',
                headers: [
                    { label: 'Cliente' },
                    { label: 'Total comprado' },
                    { label: 'Ticket médio' },
                ],
                rows: clientesRows,
                emptyMessage: 'Sem clientes para referência.',
            })}
        `;
    };

    const buildQuantidadeModal = () => {
        const periodoRows = vendasPeriodo.map((item) => ([
            { value: escapeHtml(item.label) },
            { value: formatNumber(item.quantidade), className: 'kpi-modal-number' },
            { value: formatCurrency(item.receita), className: 'kpi-modal-number' },
        ]));

        const clientesRows = clientesMaisCompram.map((item) => ([
            { value: `${escapeHtml(item.cliente_nome)}${item.cliente_codigo ? ` <small>#${escapeHtml(item.cliente_codigo)}</small>` : ''}` },
            { value: formatNumber(item.quantidade_vendas), className: 'kpi-modal-number' },
            { value: formatCurrency(item.total_comprado), className: 'kpi-modal-number' },
        ]));

        return `
            <p class="kpi-modal-intro">Período analisado: ${escapeHtml(resumo.periodo?.inicio || '-')} até ${escapeHtml(resumo.periodo?.fim || '-')}</p>
            <div class="kpi-modal-summary">
                ${summaryItem('Quantidade total de vendas', formatNumber(resumo.quantidade_vendas))}
                ${summaryItem('Total vendido', formatCurrency(resumo.total_vendas))}
                ${summaryItem('Ticket médio', formatCurrency(resumo.ticket_medio))}
            </div>
            ${renderSection({
                title: 'Quantidade de vendas por período',
                headers: [
                    { label: 'Período' },
                    { label: 'Qtd. vendas' },
                    { label: 'Receita' },
                ],
                rows: periodoRows,
                emptyMessage: 'Sem vendas registradas.',
            })}
            ${renderSection({
                title: 'Clientes com maior frequência de compra',
                headers: [
                    { label: 'Cliente' },
                    { label: 'Compras' },
                    { label: 'Total comprado' },
                ],
                rows: clientesRows,
                emptyMessage: 'Sem clientes com compras.',
            })}
        `;
    };

    const buildTicketMedioModal = () => {
        const clientesRows = clientesMaisCompram.map((item) => ([
            { value: `${escapeHtml(item.cliente_nome)}${item.cliente_codigo ? ` <small>#${escapeHtml(item.cliente_codigo)}</small>` : ''}` },
            { value: formatNumber(item.quantidade_vendas), className: 'kpi-modal-number' },
            { value: formatCurrency(item.total_comprado), className: 'kpi-modal-number' },
            { value: formatCurrency(item.ticket_medio), className: 'kpi-modal-number' },
        ]));

        const baseRows = tabelaClientes.map((item) => ([
            { value: `${escapeHtml(item.cliente_nome)}${item.cliente_codigo ? ` <small>#${escapeHtml(item.cliente_codigo)}</small>` : ''}` },
            { value: formatCurrency(item.total_comprado), className: 'kpi-modal-number' },
            { value: formatCurrency(item.total_pago), className: 'kpi-modal-number' },
            { value: formatCurrency(item.saldo_em_aberto), className: 'kpi-modal-number' },
        ]));

        return `
            <p class="kpi-modal-intro">Período analisado: ${escapeHtml(resumo.periodo?.inicio || '-')} até ${escapeHtml(resumo.periodo?.fim || '-')}</p>
            <div class="kpi-modal-summary">
                ${summaryItem('Ticket médio', formatCurrency(resumo.ticket_medio))}
                ${summaryItem('Total de vendas', formatCurrency(resumo.total_vendas))}
                ${summaryItem('Quantidade de vendas', formatNumber(resumo.quantidade_vendas))}
            </div>
            ${renderSection({
                title: 'Clientes com maior ticket médio',
                headers: [
                    { label: 'Cliente' },
                    { label: 'Compras' },
                    { label: 'Total comprado' },
                    { label: 'Ticket médio' },
                ],
                rows: clientesRows,
                emptyMessage: 'Sem clientes com ticket médio calculado.',
            })}
            ${renderSection({
                title: 'Base completa por cliente',
                headers: [
                    { label: 'Cliente' },
                    { label: 'Total comprado' },
                    { label: 'Total pago' },
                    { label: 'Saldo em aberto' },
                ],
                rows: baseRows,
                emptyMessage: 'Sem base de clientes para o período.',
            })}
        `;
    };

    const modalBuilders = {
        total_vendas: {
            title: 'Total de Vendas',
            build: buildTotalVendasModal,
        },
        total_recebido: {
            title: 'Total Recebido',
            build: buildTotalRecebidoModal,
        },
        lucro_estimado: {
            title: 'Lucro Estimado',
            build: buildLucroModal,
        },
        quantidade_vendas: {
            title: 'Quantidade de Vendas',
            build: buildQuantidadeModal,
        },
        ticket_medio: {
            title: 'Ticket Médio',
            build: buildTicketMedioModal,
        },
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
