// Espera o DOM carregar para evitar erros
document.addEventListener('DOMContentLoaded', function() {
        const formatCurrency = (window.VAFormatters && typeof window.VAFormatters.formatCurrencyBRL === 'function')
            ? window.VAFormatters.formatCurrencyBRL
            : (value) => `R$ ${Number(value || 0).toFixed(2).replace('.', ',')}`;

        const dataElement = document.getElementById('dashboard-financeiro-data');
        if (!dataElement || typeof Chart === 'undefined') {
            return;
        }

        let dashboardData;
        try {
            dashboardData = JSON.parse(dataElement.textContent);
        } catch (error) {
            console.error('Erro ao parsear dashboard-financeiro-data:', error);
            return;
        }

        const meses = dashboardData.meses || [];
        const faturamentoData = dashboardData.faturamentoData || [];
        const lucroData = dashboardData.lucroData || [];

        // Configuração padrão dos gráficos
        Chart.defaults.font.family = 'Inter, sans-serif';
        Chart.defaults.font.size = 12;
        Chart.defaults.color = '#64748b';
        
        // Animação suave nos cards ao carregar
        const cards = document.querySelectorAll('.stat-card, .chart-card');
        cards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            setTimeout(() => {
                card.style.transition = 'all 0.5s ease';
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, index * 100);
        });

        // Gráfico de Faturamento
        const ctxFaturamento = document.getElementById('chartFaturamento');
        if (ctxFaturamento) {
            new Chart(ctxFaturamento.getContext('2d'), {
                type: 'bar',
                data: {
                    labels: meses,
                    datasets: [{
                        label: 'Faturamento (R$)',
                        data: faturamentoData,
                        backgroundColor: function(context) {
                            const chart = context.chart;
                            const {ctx, chartArea} = chart;
                            if (!chartArea) return '#4F46E5';
                            const gradient = ctx.createLinearGradient(0, chartArea.bottom, 0, chartArea.top);
                            gradient.addColorStop(0, '#4F46E5');
                            gradient.addColorStop(1, '#7C3AED');
                            return gradient;
                        },
                        borderRadius: 8,
                        barThickness: 40
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            backgroundColor: '#1e293b',
                            padding: 12,
                            titleColor: '#fff',
                            bodyColor: '#fff',
                            borderColor: '#e2e8f0',
                            borderWidth: 1,
                            displayColors: false,
                            callbacks: {
                                label: (context) => formatCurrency(context.parsed.y)
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: { color: '#f1f5f9' },
                            ticks: {
                                callback: (value) => formatCurrency(value)
                            }
                        },
                        x: {
                            grid: { display: false }
                        }
                    }
                }
            });
        }

        // Gráfico de Lucro
        const ctxLucro = document.getElementById('chartLucro');
        if (ctxLucro) {
            new Chart(ctxLucro.getContext('2d'), {
                type: 'line',
                data: {
                    labels: meses,
                    datasets: [{
                        label: 'Lucro (R$)',
                        data: lucroData,
                        borderColor: '#10B981',
                        backgroundColor: function(context) {
                            const chart = context.chart;
                            const {ctx, chartArea} = chart;
                            if (!chartArea) return 'rgba(16, 185, 129, 0.1)';
                            const gradient = ctx.createLinearGradient(0, chartArea.bottom, 0, chartArea.top);
                            gradient.addColorStop(0, 'rgba(16, 185, 129, 0.05)');
                            gradient.addColorStop(1, 'rgba(16, 185, 129, 0.3)');
                            return gradient;
                        },
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4,
                        pointBackgroundColor: '#10B981',
                        pointBorderColor: '#fff',
                        pointBorderWidth: 3,
                        pointRadius: 6,
                        pointHoverRadius: 8,
                        pointHoverBackgroundColor: '#059669',
                        pointHoverBorderWidth: 3
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            backgroundColor: '#1e293b',
                            padding: 12,
                            titleColor: '#fff',
                            bodyColor: '#fff',
                            borderColor: '#e2e8f0',
                            borderWidth: 1,
                            displayColors: false,
                            callbacks: {
                                label: (context) => formatCurrency(context.parsed.y)
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: { color: '#f1f5f9' },
                            ticks: {
                                callback: (value) => formatCurrency(value)
                            }
                        },
                        x: {
                            grid: { display: false }
                        }
                    }
                }
            });
        }

        // Gráfico Comparativo
        const ctxComparativo = document.getElementById('chartComparativo');
        if (ctxComparativo) {
            new Chart(ctxComparativo.getContext('2d'), {
                type: 'bar',
                data: {
                    labels: meses,
                    datasets: [
                        {
                            label: 'Faturamento (R$)',
                            data: faturamentoData,
                            backgroundColor: function(context) {
                                const chart = context.chart;
                                const {ctx, chartArea} = chart;
                                if (!chartArea) return '#4F46E5';
                                const gradient = ctx.createLinearGradient(0, chartArea.bottom, 0, chartArea.top);
                                gradient.addColorStop(0, '#4F46E5');
                                gradient.addColorStop(1, '#7C3AED');
                                return gradient;
                            },
                            borderRadius: 8,
                            barThickness: 30
                        },
                        {
                            label: 'Lucro (R$)',
                            data: lucroData,
                            backgroundColor: function(context) {
                                const chart = context.chart;
                                const {ctx, chartArea} = chart;
                                if (!chartArea) return '#10B981';
                                const gradient = ctx.createLinearGradient(0, chartArea.bottom, 0, chartArea.top);
                                gradient.addColorStop(0, '#10B981');
                                gradient.addColorStop(1, '#059669');
                                return gradient;
                            },
                            borderRadius: 8,
                            barThickness: 30
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: true,
                            position: 'bottom',
                            labels: {
                                padding: 20,
                                usePointStyle: true,
                                pointStyle: 'circle'
                            }
                        },
                        tooltip: {
                            backgroundColor: '#1e293b',
                            padding: 12,
                            titleColor: '#fff',
                            bodyColor: '#fff',
                            borderColor: '#e2e8f0',
                            borderWidth: 1,
                            callbacks: {
                                label: (context) => `${context.dataset.label}: ${formatCurrency(context.parsed.y)}`
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: { color: '#f1f5f9' },
                            ticks: {
                                callback: (value) => formatCurrency(value)
                            }
                        },
                        x: {
                            grid: { display: false }
                        }
                    }
                }
            });
        }
    });


