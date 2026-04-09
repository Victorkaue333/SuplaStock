document.addEventListener('DOMContentLoaded', () => {
    const chartDataElement = document.getElementById('fluxo-caixa-chart-data');
    const chartMovimentacaoCanvas = document.getElementById('chartFluxoMovimentacao');
    const chartSaldoCanvas = document.getElementById('chartFluxoSaldo');

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

    if (chartDataElement && (chartMovimentacaoCanvas || chartSaldoCanvas) && typeof Chart !== 'undefined') {
        let chartPayload;
        try {
            chartPayload = JSON.parse(chartDataElement.textContent);
        } catch (error) {
            console.error('Falha ao ler dados do gráfico de fluxo de caixa:', error);
            chartPayload = null;
        }

        if (chartPayload) {
            const movimentoChart = chartPayload.movimento || {};
            const saldoChart = chartPayload.saldo || {};

            const labelsMovimento = movimentoChart.labels || chartPayload.labels || [];
            const entradas = movimentoChart.entradas || chartPayload.entradas || [];
            const saidas = movimentoChart.saidas || chartPayload.saidas || [];

            const labelsSaldo = saldoChart.labels || labelsMovimento;
            const saldos = saldoChart.saldos || chartPayload.saldo || [];

            if (chartMovimentacaoCanvas) {
                new Chart(chartMovimentacaoCanvas.getContext('2d'), {
                    type: 'bar',
                    data: {
                        labels: labelsMovimento,
                        datasets: [
                            {
                                label: 'Entradas',
                                data: entradas,
                                backgroundColor: 'rgba(5, 150, 105, 0.78)',
                                borderColor: 'rgba(5, 150, 105, 1)',
                                borderWidth: 1,
                                borderRadius: 8,
                                maxBarThickness: 44,
                                categoryPercentage: 0.64,
                                barPercentage: 0.9,
                            },
                            {
                                label: 'Saídas',
                                data: saidas,
                                backgroundColor: 'rgba(220, 38, 38, 0.75)',
                                borderColor: 'rgba(220, 38, 38, 1)',
                                borderWidth: 1,
                                borderRadius: 8,
                                maxBarThickness: 44,
                                categoryPercentage: 0.64,
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
                                position: 'bottom',
                                labels: {
                                    usePointStyle: true,
                                    pointStyle: 'circle',
                                },
                            },
                            tooltip: {
                                callbacks: {
                                    label: (ctx) => `${ctx.dataset.label}: ${formatCurrency(ctx.parsed.y)}`,
                                },
                            },
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                grid: {
                                    color: 'rgba(148, 163, 184, 0.18)',
                                },
                                ticks: {
                                    callback: (value) => formatCurrencyCompact(value),
                                    maxTicksLimit: 6,
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

            if (chartSaldoCanvas) {
                const saldoBounds = calculateBounds(saldos, { includeZero: false, paddingRatio: 0.12 });
                new Chart(chartSaldoCanvas.getContext('2d'), {
                    type: 'line',
                    data: {
                        labels: labelsSaldo,
                        datasets: [
                            {
                                label: 'Saldo acumulado',
                                data: saldos,
                                borderColor: '#1d4ed8',
                                backgroundColor: 'rgba(29, 78, 216, 0.1)',
                                borderWidth: 2.5,
                                pointRadius: 3,
                                pointHoverRadius: 4,
                                fill: true,
                                tension: 0.2,
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
                                    label: (ctx) => `Saldo: ${formatCurrency(ctx.parsed.y)}`,
                                },
                            },
                        },
                        scales: {
                            y: {
                                beginAtZero: false,
                                suggestedMin: saldoBounds.min - saldoBounds.padding,
                                suggestedMax: saldoBounds.max + saldoBounds.padding,
                                grid: {
                                    color: 'rgba(148, 163, 184, 0.18)',
                                },
                                ticks: {
                                    callback: (value) => formatCurrencyCompact(value),
                                    maxTicksLimit: 6,
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

    const kpiDataElement = document.getElementById('fluxo-caixa-kpi-data');
    const modalElement = document.getElementById('fluxoKpiModal');
    const modalTitle = document.getElementById('fluxoKpiModalTitle');
    const modalContent = document.getElementById('fluxoKpiModalContent');
    const kpiCards = document.querySelectorAll('.fluxo-kpi[data-kpi]');

    if (!kpiDataElement || !modalElement || !modalTitle || !modalContent || !kpiCards.length || typeof bootstrap === 'undefined') {
        return;
    }

    let kpiPayload;
    try {
        kpiPayload = JSON.parse(kpiDataElement.textContent);
    } catch (error) {
        console.error('Falha ao ler dados dos modais de KPI do fluxo:', error);
        return;
    }

    const modal = new bootstrap.Modal(modalElement);
    const resumo = kpiPayload.resumo || {};
    const movimentacoes = Array.isArray(kpiPayload.movimentacoes) ? kpiPayload.movimentacoes : [];
    const categoriasEntrada = Array.isArray(kpiPayload.categorias_entrada) ? kpiPayload.categorias_entrada : [];
    const categoriasSaida = Array.isArray(kpiPayload.categorias_saida) ? kpiPayload.categorias_saida : [];
    const serieFluxo = Array.isArray(kpiPayload.serie_fluxo) ? kpiPayload.serie_fluxo : [];

    const escapeHtml = (value) => String(value ?? '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');

    const summaryItem = (label, value) => `
        <article class="fluxo-kpi-summary-item">
            <span>${escapeHtml(label)}</span>
            <strong>${escapeHtml(value)}</strong>
        </article>
    `;

    const renderSection = ({ title, headers, rows, emptyMessage }) => {
        if (!rows.length) {
            return `
                <section class="fluxo-kpi-modal-section">
                    <h6>${escapeHtml(title)}</h6>
                    <p class="fluxo-kpi-modal-empty">${escapeHtml(emptyMessage || 'Sem dados disponíveis.')}</p>
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
            <section class="fluxo-kpi-modal-section">
                <h6>${escapeHtml(title)}</h6>
                <div class="fluxo-kpi-modal-table-wrap">
                    <table class="fluxo-kpi-modal-table">
                        <thead><tr>${head}</tr></thead>
                        <tbody>${body}</tbody>
                    </table>
                </div>
            </section>
        `;
    };

    const sortMovimentosDesc = (items) => [...items].sort((a, b) => {
        const dataA = a.data_iso || '';
        const dataB = b.data_iso || '';
        if (dataA !== dataB) {
            return dataA < dataB ? 1 : -1;
        }
        return Number(b.sequencia || 0) - Number(a.sequencia || 0);
    });

    const aggregateCategories = (items, tipo) => {
        const buckets = {};
        items.forEach((item) => {
            if (tipo && item.tipo !== tipo) {
                return;
            }
            const categoria = item.categoria_display || '-';
            if (!buckets[categoria]) {
                buckets[categoria] = { categoria, valor: 0, quantidade: 0 };
            }
            buckets[categoria].valor += Number(item.valor || 0);
            buckets[categoria].quantidade += 1;
        });
        return Object.values(buckets).sort((a, b) => (b.valor - a.valor) || (b.quantidade - a.quantidade));
    };

    const mapCategoryRows = (items) => items.map((item) => ([
        { value: escapeHtml(item.categoria) },
        { value: formatNumber(item.quantidade), className: 'fluxo-kpi-modal-number' },
        { value: formatCurrency(item.valor), className: 'fluxo-kpi-modal-number' },
    ]));

    const mapSerieRows = (items) => items.map((item) => ([
        { value: escapeHtml(item.label || '-') },
        { value: formatCurrency(item.entrada), className: 'fluxo-kpi-modal-number' },
        { value: formatCurrency(item.saida), className: 'fluxo-kpi-modal-number' },
        { value: formatCurrency(item.saldo), className: 'fluxo-kpi-modal-number' },
    ]));

    const mapMovimentoRows = (items) => items.map((item) => {
        const tipo = item.tipo === 'saida' ? 'saida' : 'entrada';
        const tipoClass = tipo === 'saida' ? 'tipo-saida' : 'tipo-entrada';
        const valorPrefixo = tipo === 'entrada' ? '+' : '-';
        return [
            { value: escapeHtml(item.data || '-') },
            { value: `<span class="tipo-badge ${tipoClass}">${escapeHtml(item.tipo_display || tipo)}</span>` },
            { value: escapeHtml(item.categoria_display || '-') },
            { value: escapeHtml(item.descricao || '-') },
            { value: `${valorPrefixo}${formatCurrency(item.valor)}`, className: 'fluxo-kpi-modal-number' },
            { value: escapeHtml(item.origem || '-') },
            { value: escapeHtml(item.usuario || '-') },
            { value: formatCurrency(item.saldo_acumulado), className: 'fluxo-kpi-modal-number' },
        ];
    });

    const movimentosEntrada = sortMovimentosDesc(movimentacoes.filter((item) => item.tipo === 'entrada'));
    const movimentosSaida = sortMovimentosDesc(movimentacoes.filter((item) => item.tipo === 'saida'));
    const movimentosOrdenados = sortMovimentosDesc(movimentacoes);
    const movimentosHoje = movimentosOrdenados.filter((item) => item.data_iso === resumo.hoje_iso);
    const movimentosMes = movimentosOrdenados.filter((item) => (item.data_iso || '').startsWith(resumo.mes_referencia || ''));

    const categoriasHojeEntrada = aggregateCategories(movimentosHoje, 'entrada');
    const categoriasHojeSaida = aggregateCategories(movimentosHoje, 'saida');
    const categoriasMesEntrada = aggregateCategories(movimentosMes, 'entrada');
    const categoriasMesSaida = aggregateCategories(movimentosMes, 'saida');

    const buildEntradasModal = () => `
        <p class="fluxo-kpi-modal-intro">Período analisado: ${escapeHtml(resumo.periodo?.inicio || '-')} até ${escapeHtml(resumo.periodo?.fim || '-')}</p>
        <div class="fluxo-kpi-modal-summary">
            ${summaryItem('Entradas no período', formatCurrency(resumo.total_entradas_periodo))}
            ${summaryItem('Lançamentos de entrada', formatNumber(movimentosEntrada.length))}
            ${summaryItem('Saldo no período', formatCurrency(resumo.saldo_periodo))}
        </div>
        ${renderSection({
            title: 'Entradas por categoria',
            headers: [{ label: 'Categoria' }, { label: 'Lançamentos' }, { label: 'Total' }],
            rows: mapCategoryRows(categoriasEntrada),
            emptyMessage: 'Sem entradas no período.',
        })}
        ${renderSection({
            title: 'Lançamentos de entrada',
            headers: [
                { label: 'Data' }, { label: 'Tipo' }, { label: 'Categoria' }, { label: 'Descrição' },
                { label: 'Valor' }, { label: 'Origem' }, { label: 'Usuário' }, { label: 'Saldo acumulado' },
            ],
            rows: mapMovimentoRows(movimentosEntrada),
            emptyMessage: 'Sem lançamentos de entrada.',
        })}
    `;

    const buildSaidasModal = () => `
        <p class="fluxo-kpi-modal-intro">Período analisado: ${escapeHtml(resumo.periodo?.inicio || '-')} até ${escapeHtml(resumo.periodo?.fim || '-')}</p>
        <div class="fluxo-kpi-modal-summary">
            ${summaryItem('Saídas no período', formatCurrency(resumo.total_saidas_periodo))}
            ${summaryItem('Lançamentos de saída', formatNumber(movimentosSaida.length))}
            ${summaryItem('Saldo no período', formatCurrency(resumo.saldo_periodo))}
        </div>
        ${renderSection({
            title: 'Saídas por categoria',
            headers: [{ label: 'Categoria' }, { label: 'Lançamentos' }, { label: 'Total' }],
            rows: mapCategoryRows(categoriasSaida),
            emptyMessage: 'Sem saídas no período.',
        })}
        ${renderSection({
            title: 'Lançamentos de saída',
            headers: [
                { label: 'Data' }, { label: 'Tipo' }, { label: 'Categoria' }, { label: 'Descrição' },
                { label: 'Valor' }, { label: 'Origem' }, { label: 'Usuário' }, { label: 'Saldo acumulado' },
            ],
            rows: mapMovimentoRows(movimentosSaida),
            emptyMessage: 'Sem lançamentos de saída.',
        })}
    `;

    const buildSaldoAtualModal = () => `
        <p class="fluxo-kpi-modal-intro">Período analisado: ${escapeHtml(resumo.periodo?.inicio || '-')} até ${escapeHtml(resumo.periodo?.fim || '-')}</p>
        <div class="fluxo-kpi-modal-summary">
            ${summaryItem('Saldo atual', formatCurrency(resumo.saldo_atual))}
            ${summaryItem('Saldo início do período', formatCurrency(resumo.saldo_inicio_periodo))}
            ${summaryItem('Saldo final do período', formatCurrency(resumo.saldo_final_periodo))}
            ${summaryItem('Variação no período', formatCurrency(resumo.saldo_periodo))}
        </div>
        ${renderSection({
            title: 'Evolução do caixa (período)',
            headers: [{ label: 'Período' }, { label: 'Entradas' }, { label: 'Saídas' }, { label: 'Saldo' }],
            rows: mapSerieRows(serieFluxo),
            emptyMessage: 'Sem série de evolução para o período.',
        })}
        ${renderSection({
            title: 'Movimentações do período',
            headers: [
                { label: 'Data' }, { label: 'Tipo' }, { label: 'Categoria' }, { label: 'Descrição' },
                { label: 'Valor' }, { label: 'Origem' }, { label: 'Usuário' }, { label: 'Saldo acumulado' },
            ],
            rows: mapMovimentoRows(movimentosOrdenados),
            emptyMessage: 'Sem movimentações no período.',
        })}
    `;

    const buildSaldoDiaModal = () => `
        <p class="fluxo-kpi-modal-intro">Referência do dia: ${escapeHtml(resumo.hoje_iso || '-')}</p>
        <div class="fluxo-kpi-modal-summary">
            ${summaryItem('Saldo do dia', formatCurrency(resumo.saldo_dia))}
            ${summaryItem('Entradas do dia', formatCurrency(resumo.entradas_hoje))}
            ${summaryItem('Saídas do dia', formatCurrency(resumo.saidas_hoje))}
            ${summaryItem('Movimentações do dia', formatNumber(movimentosHoje.length))}
        </div>
        ${renderSection({
            title: 'Entradas do dia por categoria',
            headers: [{ label: 'Categoria' }, { label: 'Lançamentos' }, { label: 'Total' }],
            rows: mapCategoryRows(categoriasHojeEntrada),
            emptyMessage: 'Sem entradas no dia.',
        })}
        ${renderSection({
            title: 'Saídas do dia por categoria',
            headers: [{ label: 'Categoria' }, { label: 'Lançamentos' }, { label: 'Total' }],
            rows: mapCategoryRows(categoriasHojeSaida),
            emptyMessage: 'Sem saídas no dia.',
        })}
        ${renderSection({
            title: 'Lançamentos do dia',
            headers: [
                { label: 'Data' }, { label: 'Tipo' }, { label: 'Categoria' }, { label: 'Descrição' },
                { label: 'Valor' }, { label: 'Origem' }, { label: 'Usuário' }, { label: 'Saldo acumulado' },
            ],
            rows: mapMovimentoRows(movimentosHoje),
            emptyMessage: 'Sem movimentações no dia.',
        })}
    `;

    const buildSaldoMesModal = () => `
        <p class="fluxo-kpi-modal-intro">Referência do mês: ${escapeHtml(resumo.mes_referencia || '-')}</p>
        <div class="fluxo-kpi-modal-summary">
            ${summaryItem('Saldo do mês', formatCurrency(resumo.saldo_mes))}
            ${summaryItem('Entradas do mês', formatCurrency(resumo.entradas_mes))}
            ${summaryItem('Saídas do mês', formatCurrency(resumo.saidas_mes))}
            ${summaryItem('Movimentações do mês', formatNumber(movimentosMes.length))}
        </div>
        ${renderSection({
            title: 'Entradas do mês por categoria',
            headers: [{ label: 'Categoria' }, { label: 'Lançamentos' }, { label: 'Total' }],
            rows: mapCategoryRows(categoriasMesEntrada),
            emptyMessage: 'Sem entradas no mês.',
        })}
        ${renderSection({
            title: 'Saídas do mês por categoria',
            headers: [{ label: 'Categoria' }, { label: 'Lançamentos' }, { label: 'Total' }],
            rows: mapCategoryRows(categoriasMesSaida),
            emptyMessage: 'Sem saídas no mês.',
        })}
        ${renderSection({
            title: 'Lançamentos do mês',
            headers: [
                { label: 'Data' }, { label: 'Tipo' }, { label: 'Categoria' }, { label: 'Descrição' },
                { label: 'Valor' }, { label: 'Origem' }, { label: 'Usuário' }, { label: 'Saldo acumulado' },
            ],
            rows: mapMovimentoRows(movimentosMes),
            emptyMessage: 'Sem movimentações no mês.',
        })}
    `;

    const modalBuilders = {
        entradas_periodo: { title: 'Entradas no Período', build: buildEntradasModal },
        saidas_periodo: { title: 'Saídas no Período', build: buildSaidasModal },
        saldo_atual: { title: 'Saldo Atual', build: buildSaldoAtualModal },
        saldo_dia: { title: 'Saldo do Dia', build: buildSaldoDiaModal },
        saldo_mes: { title: 'Saldo do Mês', build: buildSaldoMesModal },
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
