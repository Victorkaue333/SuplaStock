function abrirModalExportacaoPDF() {
        var modal = new bootstrap.Modal(document.getElementById('modalExportacaoPDF'));
        modal.show();
    }
    function fecharModalExportacaoPDF() {
        var modalEl = document.getElementById('modalExportacaoPDF');
        var modal = bootstrap.Modal.getInstance(modalEl);
        if (modal) modal.hide();
    }
    function exportarPDFTodasVendas() {
        mostrarLoading();
        setTimeout(function() { // Simula carregamento
            try {
                const doc = new window.jspdf.jsPDF({ orientation: 'landscape', unit: 'pt', format: 'a4' });
                doc.setFontSize(20);
                doc.setFont('helvetica', 'bold');
                doc.text('Relatório de Todas as Notas Fiscais', 40, 40);
                const head = [[
                    'Data da Venda', 'Cliente', 'Produto', 'Quantidade', 'Valor Unitário', 'Valor Total'
                ]];
                const body = [];
                document.querySelectorAll('.responsive-table tbody tr').forEach(function(row) {
                    const cols = row.querySelectorAll('td');
                    if (cols.length >= 6) {
                        body.push([
                            cols[0].innerText,
                            cols[1].innerText,
                            cols[2].innerText,
                            cols[3].innerText,
                            cols[4].innerText,
                            cols[5].innerText
                        ]);
                    }
                });
                doc.autoTable({
                    head: head,
                    body: body,
                    startY: 62,
                    styles: { font: 'helvetica', fontSize: 11, cellPadding: 6 },
                    headStyles: { fillColor: [102, 126, 234], textColor: 255, fontStyle: 'bold', halign: 'center' },
                    bodyStyles: { textColor: 34 },
                    columnStyles: {
                        0: { cellWidth: 90 },
                        1: { cellWidth: 120 },
                        2: { cellWidth: 120 },
                        3: { cellWidth: 70, halign: 'center' },
                        4: { cellWidth: 90, halign: 'right' },
                        5: { cellWidth: 100, halign: 'right' }
                    },
                    didDrawPage: function (data) {
                        var str = 'Página ' + doc.internal.getNumberOfPages();
                        doc.setFontSize(10);
                        doc.text(str, doc.internal.pageSize.getWidth() - 60, doc.internal.pageSize.getHeight() - 20);
                    }
                });
                doc.save('todas_notas_fiscais.pdf');
                mostrarToast('PDF exportado com sucesso!', true);
            } catch (e) {
                mostrarToast('Erro ao exportar PDF.', false);
            }
            esconderLoading();
        }, 400);
    }
