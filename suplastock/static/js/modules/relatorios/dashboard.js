document.addEventListener('DOMContentLoaded', function() {
    const chartElement = document.getElementById('chartEvolucao');
    const dataElement = document.getElementById('relatorio-dashboard-data');

    if (!chartElement || !dataElement || typeof Chart === 'undefined') {
        return;
    }

    let chartData;
    try {
        chartData = JSON.parse(dataElement.textContent);
    } catch (error) {
        console.error('Erro ao parsear relatorio-dashboard-data:', error);
        return;
    }

    const labels = chartData.labels || [];
    const vendas = chartData.vendas || [];
    const receita = chartData.receita || [];

    const ctx = chartElement.getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Vendas',
                    data: vendas,
                    borderColor: '#dc3545',
                    tension: 0.3
                },
                {
                    label: 'Receita (R$)',
                    data: receita,
                    borderColor: '#198754',
                    tension: 0.3,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                y: { beginAtZero: true, position: 'left' },
                y1: { beginAtZero: true, position: 'right', grid: { drawOnChartArea: false } }
            }
        }
    });
});
