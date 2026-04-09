(function initializeGestaoProdutos() {
    const searchInput = document.getElementById('searchInput');
    const categoryFilter = document.getElementById('categoryFilter');
    const supplierFilter = document.getElementById('supplierFilter');
    const statusFilter = document.getElementById('statusFilter');
    const priceRangeFilter = document.getElementById('priceRangeFilter');
    const sortFilter = document.getElementById('sortFilter');
    const onlyOutFilter = document.getElementById('onlyOutFilter');
    const clearStockFiltersButton = document.getElementById('clearStockFilters');

    const tableRows = Array.from(document.querySelectorAll('#productsTableBody tr[data-search]'));
    const noFilteredResultsRow = document.getElementById('noFilteredResultsRow');
    const noFilteredResultsMessage = document.getElementById('noFilteredResultsMessage');

    const stockFilterCards = Array.from(document.querySelectorAll('.stock-filter-card[data-stock-filter]'));
    const stockModalElement = document.getElementById('modalResumoEstoque');
    const stockModalTitle = document.getElementById('stockStatusModalTitle');
    const stockModalSubtitle = document.getElementById('stockStatusModalSubtitle');
    const stockModalBody = document.getElementById('stockStatusModalBody');
    const stockModalEmpty = document.getElementById('stockStatusModalEmpty');
    const stockModalEmptyMessage = document.getElementById('stockStatusModalEmptyMessage');
    const stockModalTableWrapper = document.getElementById('stockStatusModalTableWrapper');
    const stockModalSearchInput = document.getElementById('stockModalSearchInput');

    const detalhesModalElement = document.getElementById('modalDetalhesProduto');
    const cadastrarModalElement = document.getElementById('modalCadastrarProduto');

    const produtosConfig = document.getElementById('produtos-route-config');
    const apiProdutosUrl = produtosConfig ? produtosConfig.dataset.apiProdutosUrl : null;
    const apiSkuPreviewUrl = produtosConfig ? produtosConfig.dataset.apiSkuPreviewUrl : null;

    const formCadastrar = document.getElementById('formCadastrar');
    const createNomeInput = formCadastrar?.querySelector('input[name="nome"]');
    const createSkuInput = formCadastrar?.querySelector('input[name="sku"]');

    let todosProdutos = null;
    let produtosCarregando = false;
    let produtosFiltradosModal = [];
    let currentFilterType = 'all';

    const stockModal = (stockModalElement && window.bootstrap)
        ? new bootstrap.Modal(stockModalElement)
        : null;

    const detalhesModal = (detalhesModalElement && window.bootstrap)
        ? new bootstrap.Modal(detalhesModalElement)
        : null;

    const escapeHtml = (value) => String(value || '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');

    const parseDecimalFromString = (value) => {
        if (typeof value === 'number') {
            return Number.isFinite(value) ? value : 0;
        }
        let normalized = String(value || '').trim();
        normalized = normalized.replace(/[^\d,.-]/g, '');
        if (normalized.includes(',') && normalized.includes('.')) {
            normalized = normalized.replace(/\./g, '').replace(',', '.');
        } else if (normalized.includes(',')) {
            normalized = normalized.replace(',', '.');
        }
        const parsed = Number.parseFloat(normalized);
        return Number.isFinite(parsed) ? parsed : 0;
    };

    const formatCurrencyBr = (value) => `R$ ${Number(value || 0).toFixed(2).replace('.', ',')}`;
    const formatPercentBr = (value) => `${Number(value || 0).toFixed(2).replace('.', ',')}%`;

    const fallbackSku = (nome) => {
        const base = String(nome || '')
            .toUpperCase()
            .replace(/[^A-Z0-9]/g, '')
            .slice(0, 3) || 'PRD';
        return `${base}-001`;
    };

    const getStatusInfo = (currentStockRaw, minimumStockRaw) => {
        const currentStock = Number.parseInt(currentStockRaw || 0, 10);
        const minimumStock = Number.parseInt(minimumStockRaw || 0, 10);

        if (currentStock === 0) {
            return { code: 'esgotado', label: 'Esgotado', className: 'out' };
        }
        if (currentStock <= minimumStock) {
            return { code: 'critico', label: 'Crítico', className: 'critical' };
        }
        if (currentStock <= (minimumStock + 3)) {
            return { code: 'baixo', label: 'Baixo', className: 'low' };
        }
        return { code: 'normal', label: 'Normal', className: 'ok' };
    };

    const getProdutoStockValue = (produto) => {
        const currentStock = Number.parseInt(produto.estoque_atual || 0, 10);
        const costUnit = parseDecimalFromString(produto.preco_custo_unitario || '0');
        return currentStock * costUnit;
    };

    const carregarTodosProdutos = async () => {
        if (todosProdutos !== null) {
            return todosProdutos;
        }

        if (produtosCarregando) {
            for (let i = 0; i < 50; i += 1) {
                await new Promise((resolve) => setTimeout(resolve, 100));
                if (todosProdutos !== null) {
                    return todosProdutos;
                }
            }
            throw new Error('Timeout ao carregar produtos');
        }

        if (!apiProdutosUrl) {
            throw new Error('URL da API de produtos não configurada');
        }

        produtosCarregando = true;
        try {
            const response = await fetch(apiProdutosUrl, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    Accept: 'application/json',
                },
                credentials: 'same-origin',
            });

            if (!response.ok) {
                throw new Error(`Erro HTTP: ${response.status}`);
            }

            const data = await response.json();
            todosProdutos = data.produtos || [];
            return todosProdutos;
        } finally {
            produtosCarregando = false;
        }
    };

    const getModalConfig = (filterType, count, totalValue = 0) => {
        if (filterType === 'all') {
            return {
                title: 'Todos os Produtos em Estoque',
                subtitle: `${count} produto(s) cadastrado(s)`,
                emptyText: 'Nenhum produto cadastrado.',
            };
        }

        if (filterType === 'value') {
            return {
                title: 'Valor em Estoque por Produto',
                subtitle: `${count} produto(s) • valor total ${formatCurrencyBr(totalValue)}`,
                emptyText: 'Nenhum produto com valor em estoque.',
            };
        }

        if (filterType === 'critical') {
            return {
                title: 'Produtos com Estoque Crítico',
                subtitle: `${count} produto(s) em nível crítico`,
                emptyText: 'Nenhum produto com estoque crítico.',
            };
        }

        if (filterType === 'low') {
            return {
                title: 'Produtos com Estoque Baixo',
                subtitle: `${count} produto(s) com nível baixo`,
                emptyText: 'Nenhum produto com estoque baixo.',
            };
        }

        return {
            title: 'Produtos Esgotados',
            subtitle: `${count} produto(s) com estoque zerado`,
            emptyText: 'Nenhum produto esgotado.',
        };
    };

    const produtoStockConditionMatches = (produto, filterType) => {
        const status = getStatusInfo(produto.estoque_atual, produto.estoque_minimo);

        if (filterType === 'all' || filterType === 'value') {
            return true;
        }
        if (filterType === 'critical') {
            return status.code === 'critico';
        }
        if (filterType === 'low') {
            return status.code === 'baixo';
        }
        if (filterType === 'out') {
            return status.code === 'esgotado';
        }

        return false;
    };

    const renderStockModalRows = (lista, filterType) => {
        const bodyHtml = lista.map((produto) => {
            const name = escapeHtml(produto.nome || '-');
            const sku = escapeHtml(produto.sku || '-');
            const category = escapeHtml(produto.categoria_nome || 'Sem categoria');
            const currentStock = Number.parseInt(produto.estoque_atual || 0, 10);
            const minimumStock = Number.parseInt(produto.estoque_minimo || 0, 10);
            const stockValue = getProdutoStockValue(produto);

            let status = getStatusInfo(currentStock, minimumStock);
            if (filterType === 'value') {
                status = { className: 'ok', label: formatCurrencyBr(stockValue) };
            }

            return `
                <tr>
                    <td style="padding: 12px 16px; font-weight: 600; color: #1e293b;">${name}<div style="font-size:11px;color:#64748b;">${sku}</div></td>
                    <td style="padding: 12px 16px; color: #475569;">${category}</td>
                    <td style="padding: 12px 16px; text-align: center; font-weight: 700;">${currentStock}</td>
                    <td style="padding: 12px 16px; text-align: center; color: #475569;">${minimumStock}</td>
                    <td style="padding: 12px 16px; text-align: center;">
                        <span class="stock-status-badge ${status.className}">${status.label}</span>
                    </td>
                </tr>
            `;
        }).join('');

        stockModalBody.innerHTML = bodyHtml;
        stockModalEmpty.style.display = 'none';
        stockModalTableWrapper.style.display = '';
    };

    const openStockStatusModal = async (filterType) => {
        if (!stockModal || !stockModalBody || !stockModalTitle || !stockModalSubtitle || !stockModalEmpty || !stockModalEmptyMessage || !stockModalTableWrapper) {
            return;
        }

        if (stockModalSearchInput) {
            stockModalSearchInput.value = '';
        }

        stockModalTitle.textContent = 'Carregando produtos...';
        stockModalSubtitle.textContent = 'Aguarde um momento';
        stockModalBody.innerHTML = '';
        stockModalEmpty.style.display = '';
        stockModalEmptyMessage.textContent = 'Carregando dados...';
        stockModalTableWrapper.style.display = 'none';
        stockModal.show();

        try {
            const produtos = await carregarTodosProdutos();
            let matchedProdutos = produtos.filter((produto) => produtoStockConditionMatches(produto, filterType));
            const totalValue = matchedProdutos.reduce((acc, produto) => acc + getProdutoStockValue(produto), 0);

            if (filterType === 'value') {
                matchedProdutos = matchedProdutos.sort((a, b) => getProdutoStockValue(b) - getProdutoStockValue(a));
            }

            const config = getModalConfig(filterType, matchedProdutos.length, totalValue);
            stockModalTitle.textContent = config.title;
            stockModalSubtitle.textContent = config.subtitle;

            stockFilterCards.forEach((card) => {
                const isActive = card.getAttribute('data-stock-filter') === filterType;
                card.classList.toggle('is-active', isActive);
                card.setAttribute('aria-pressed', String(isActive));
            });

            if (matchedProdutos.length === 0) {
                stockModalBody.innerHTML = '';
                stockModalEmptyMessage.textContent = config.emptyText;
                stockModalEmpty.style.display = '';
                stockModalTableWrapper.style.display = 'none';
                return;
            }

            renderStockModalRows(matchedProdutos, filterType);
            produtosFiltradosModal = matchedProdutos;
            currentFilterType = filterType;
        } catch (error) {
            console.error('Erro ao abrir modal de estoque:', error);
            stockModalTitle.textContent = 'Erro ao carregar produtos';
            stockModalSubtitle.textContent = 'Não foi possível carregar os dados';
            stockModalBody.innerHTML = '';
            stockModalEmptyMessage.textContent = 'Erro ao carregar produtos. Tente novamente.';
            stockModalEmpty.style.display = '';
            stockModalTableWrapper.style.display = 'none';
        }
    };

    const filterModalProdutos = () => {
        if (!stockModalSearchInput) {
            return;
        }

        const searchTerm = stockModalSearchInput.value.toLowerCase().trim();
        let lista = produtosFiltradosModal;

        if (searchTerm) {
            lista = produtosFiltradosModal.filter((produto) => {
                const nome = (produto.nome || '').toLowerCase();
                const categoria = (produto.categoria_nome || '').toLowerCase();
                const sku = (produto.sku || '').toLowerCase();
                return nome.includes(searchTerm) || categoria.includes(searchTerm) || sku.includes(searchTerm);
            });
        }

        if (lista.length === 0) {
            stockModalBody.innerHTML = '';
            stockModalEmptyMessage.textContent = 'Nenhum produto encontrado com o termo pesquisado.';
            stockModalEmpty.style.display = '';
            stockModalTableWrapper.style.display = 'none';
            return;
        }

        renderStockModalRows(lista, currentFilterType);
    };

    const syncFilterInputsFromUrl = () => {
        const urlParams = new URLSearchParams(window.location.search);
        if (searchInput) {
            searchInput.value = urlParams.get('search') || '';
        }
        if (categoryFilter) {
            categoryFilter.value = urlParams.get('categoria') || '';
        }
        if (supplierFilter) {
            supplierFilter.value = urlParams.get('fornecedor') || '';
        }
        if (statusFilter) {
            statusFilter.value = urlParams.get('status_estoque') || '';
        }
        if (priceRangeFilter) {
            priceRangeFilter.value = urlParams.get('faixa_preco') || '';
        }
        if (sortFilter) {
            sortFilter.value = urlParams.get('ordenar') || 'recentes';
        }
        if (onlyOutFilter) {
            const rawOnlyOut = (urlParams.get('apenas_esgotados') || '').toLowerCase();
            onlyOutFilter.checked = ['1', 'true', 'on', 'yes', 'sim'].includes(rawOnlyOut);
        }
    };

    const updateUrlWithFilters = () => {
        const url = new URL(window.location.href);
        const values = {
            search: (searchInput?.value || '').trim(),
            categoria: categoryFilter?.value || '',
            fornecedor: (supplierFilter?.value || '').trim(),
            status_estoque: statusFilter?.value || '',
            faixa_preco: priceRangeFilter?.value || '',
            ordenar: sortFilter?.value || 'recentes',
            apenas_esgotados: onlyOutFilter?.checked ? '1' : '',
        };

        Object.entries(values).forEach(([key, value]) => {
            if (value) {
                url.searchParams.set(key, value);
            } else {
                url.searchParams.delete(key);
            }
        });

        if (values.ordenar === 'recentes') {
            url.searchParams.delete('ordenar');
        }

        url.searchParams.delete('page');
        window.location.href = url.toString();
    };

    const toggleStockClearButton = () => {
        if (!clearStockFiltersButton) {
            return;
        }

        const hasActiveFilter = Boolean(
            (searchInput?.value || '').trim()
            || (categoryFilter?.value || '').trim()
            || (supplierFilter?.value || '').trim()
            || (statusFilter?.value || '').trim()
            || (priceRangeFilter?.value || '').trim()
            || (onlyOutFilter?.checked)
            || ((sortFilter?.value || 'recentes') !== 'recentes')
        );

        clearStockFiltersButton.hidden = !hasActiveFilter;
    };

    const clearStockFilters = () => {
        if (searchInput) searchInput.value = '';
        if (categoryFilter) categoryFilter.value = '';
        if (supplierFilter) supplierFilter.value = '';
        if (statusFilter) statusFilter.value = '';
        if (priceRangeFilter) priceRangeFilter.value = '';
        if (sortFilter) sortFilter.value = 'recentes';
        if (onlyOutFilter) onlyOutFilter.checked = false;
        updateUrlWithFilters();
    };

    const resolveProdutoDetalhesUrl = (id) => {
        const template = produtosConfig?.dataset.apiProdutoDetalhesTemplate || '';
        if (template.includes('/0/')) {
            return template.replace('/0/', `/${id}/`);
        }
        return '';
    };

    window.visualizarProduto = async function visualizarProduto(produtoId) {
        if (!detalhesModal) {
            return;
        }

        const detalhesUrl = resolveProdutoDetalhesUrl(produtoId);
        if (!detalhesUrl) {
            window.AppFeedback?.showToast?.('Rota de detalhes de produto não configurada.', { variant: 'danger' });
            return;
        }

        try {
            const response = await fetch(detalhesUrl, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    Accept: 'application/json',
                },
                credentials: 'same-origin',
            });

            if (!response.ok) {
                throw new Error(`Erro HTTP: ${response.status}`);
            }

            const data = await response.json();

            document.getElementById('produtoDetalheTitulo').textContent = `Detalhes - ${data.nome || '-'}`;
            document.getElementById('produtoDetalheSubtitulo').textContent = `SKU: ${data.sku || '-'} • Status: ${data.status_estoque || '-'}`;
            document.getElementById('detalhe_nome_produto').textContent = data.nome || '-';
            document.getElementById('detalhe_sku_produto').textContent = data.sku || '-';
            document.getElementById('detalhe_categoria_produto').textContent = data.categoria || '-';
            document.getElementById('detalhe_fornecedor_produto').textContent = data.fornecedor || '-';
            document.getElementById('detalhe_data_cadastro_produto').textContent = data.data_cadastro || '-';
            document.getElementById('detalhe_ultima_atualizacao_produto').textContent = data.ultima_atualizacao || '-';
            document.getElementById('detalhe_qtd_comprada_produto').textContent = data.quantidade_comprada || 0;
            document.getElementById('detalhe_qtd_vendida_produto').textContent = data.quantidade_vendida || 0;
            document.getElementById('detalhe_estoque_atual_produto').textContent = data.estoque_atual || 0;
            document.getElementById('detalhe_estoque_minimo_produto').textContent = data.estoque_minimo || 0;

            document.getElementById('detalhe_preco_custo_produto').textContent = formatCurrencyBr(data.preco_custo || 0);
            document.getElementById('detalhe_preco_venda_produto').textContent = formatCurrencyBr(data.preco_venda || 0);
            document.getElementById('detalhe_lucro_unitario_produto').textContent = formatCurrencyBr(data.lucro_unitario || 0);
            document.getElementById('detalhe_margem_produto').textContent = formatPercentBr(data.margem_lucro || 0);

            const statusEl = document.getElementById('detalhe_status_produto');
            const statusRaw = String(data.status_estoque || '').toUpperCase();
            const statusMap = {
                NORMAL: 'ok',
                BAIXO: 'low',
                'CRÍTICO': 'critical',
                CRITICO: 'critical',
                ESGOTADO: 'out',
            };
            const statusClass = statusMap[statusRaw] || 'ok';
            statusEl.className = `stock-status-badge ${statusClass}`;
            statusEl.textContent = data.status_estoque || 'NORMAL';

            const movimentosBody = document.getElementById('detalhe_movimentacoes_body');
            const historico = Array.isArray(data.historico) ? data.historico : [];

            if (!historico.length) {
                movimentosBody.innerHTML = '<tr><td colspan="5" class="text-center text-muted" style="padding:20px;">Sem movimentações registradas.</td></tr>';
            } else {
                movimentosBody.innerHTML = historico.map((mov) => {
                    const quantidade = Number(mov.quantidade || 0);
                    const quantidadeFormatada = quantidade > 0 ? `+${quantidade}` : `${quantidade}`;
                    const quantidadeCor = quantidade < 0 ? '#DC2626' : '#059669';
                    const tipoRaw = String(mov.tipo || '').toLowerCase();
                    let tipoClass = 'ok';
                    if (tipoRaw.includes('saída') || tipoRaw.includes('saida') || tipoRaw.includes('ajuste')) {
                        tipoClass = 'critical';
                    } else if (tipoRaw.includes('devolução') || tipoRaw.includes('devolucao')) {
                        tipoClass = 'low';
                    }
                    return `
                        <tr>
                            <td>${escapeHtml(mov.data || '-')}</td>
                            <td><span class="stock-status-badge ${tipoClass}">${escapeHtml(mov.tipo || '-')}</span></td>
                            <td class="text-center" style="font-weight:700;color:${quantidadeCor};">${quantidadeFormatada}</td>
                            <td>${escapeHtml(mov.responsavel || '-')}</td>
                            <td>${escapeHtml(mov.observacao || '-')}</td>
                        </tr>
                    `;
                }).join('');
            }

            detalhesModal.show();
        } catch (error) {
            console.error('Erro ao buscar detalhes do produto:', error);
            window.AppFeedback?.showToast?.('Não foi possível carregar os detalhes do produto.', { variant: 'danger' });
        }
    };

    syncFilterInputsFromUrl();
    toggleStockClearButton();

    let searchDebounceTimer = null;

    if (searchInput) {
        searchInput.addEventListener('input', () => {
            toggleStockClearButton();
            if (searchDebounceTimer) {
                clearTimeout(searchDebounceTimer);
            }
            searchDebounceTimer = setTimeout(() => {
                updateUrlWithFilters();
            }, 600);
        });

        searchInput.addEventListener('keydown', (event) => {
            if (event.key === 'Enter') {
                event.preventDefault();
                if (searchDebounceTimer) {
                    clearTimeout(searchDebounceTimer);
                }
                updateUrlWithFilters();
            }
        });
    }

    [categoryFilter, statusFilter, priceRangeFilter, sortFilter, onlyOutFilter].forEach((input) => {
        if (!input) {
            return;
        }
        input.addEventListener('change', () => {
            toggleStockClearButton();
            updateUrlWithFilters();
        });
    });

    if (supplierFilter) {
        supplierFilter.addEventListener('input', () => {
            toggleStockClearButton();
            if (searchDebounceTimer) {
                clearTimeout(searchDebounceTimer);
            }
            searchDebounceTimer = setTimeout(() => {
                updateUrlWithFilters();
            }, 600);
        });
    }

    if (clearStockFiltersButton) {
        clearStockFiltersButton.addEventListener('click', clearStockFilters);
    }

    window.abrirModalResumoEstoque = openStockStatusModal;

    if (stockModalElement) {
        stockModalElement.addEventListener('hidden.bs.modal', () => {
            stockFilterCards.forEach((card) => {
                card.classList.remove('is-active');
                card.setAttribute('aria-pressed', 'false');
            });

            if (stockModalSearchInput) {
                stockModalSearchInput.value = '';
            }

            produtosFiltradosModal = [];
            currentFilterType = 'all';
        });
    }

    if (stockModalSearchInput) {
        stockModalSearchInput.addEventListener('input', filterModalProdutos);
    }

    stockFilterCards.forEach((card) => {
        card.addEventListener('keydown', (event) => {
            if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                const filterType = card.getAttribute('data-stock-filter') || 'all';
                openStockStatusModal(filterType);
            }
        });
    });

    // Mantido para compatibilidade com fallback do template
    if (tableRows.length > 0 && noFilteredResultsRow && noFilteredResultsMessage) {
        noFilteredResultsRow.style.display = 'none';
        noFilteredResultsMessage.textContent = 'Nenhum produto encontrado com os filtros aplicados.';
    }

    if (createNomeInput && createSkuInput) {
        let skuDebounceTimer = null;
        let skuRequestToken = 0;

        const atualizarSkuPreview = () => {
            const nome = String(createNomeInput.value || '').trim();
            skuRequestToken += 1;
            const localToken = skuRequestToken;

            if (!nome) {
                createSkuInput.value = '';
                return;
            }

            if (skuDebounceTimer) {
                clearTimeout(skuDebounceTimer);
            }

            skuDebounceTimer = setTimeout(async () => {
                if (!apiSkuPreviewUrl) {
                    createSkuInput.value = fallbackSku(nome);
                    return;
                }

                try {
                    const url = new URL(apiSkuPreviewUrl, window.location.origin);
                    url.searchParams.set('nome', nome);

                    const response = await fetch(url.toString(), {
                        method: 'GET',
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest',
                            Accept: 'application/json',
                        },
                        credentials: 'same-origin',
                    });

                    if (localToken !== skuRequestToken) {
                        return;
                    }

                    if (!response.ok) {
                        throw new Error(`Erro HTTP: ${response.status}`);
                    }

                    const payload = await response.json();
                    createSkuInput.value = payload?.sku || fallbackSku(nome);
                } catch (error) {
                    console.warn('Falha ao gerar SKU automático no modal:', error);
                    if (localToken === skuRequestToken) {
                        createSkuInput.value = fallbackSku(nome);
                    }
                }
            }, 250);
        };

        createNomeInput.addEventListener('input', atualizarSkuPreview);

        if (cadastrarModalElement) {
            cadastrarModalElement.addEventListener('shown.bs.modal', () => {
                if (String(createNomeInput.value || '').trim()) {
                    atualizarSkuPreview();
                } else {
                    createSkuInput.value = '';
                }
            });
        }
    }
}());

function resolveProdutoUrl(kind, id) {
    const configElement = document.getElementById('produtos-route-config');
    const template = kind === 'edit'
        ? (configElement?.dataset.editUrlTemplate || '')
        : (configElement?.dataset.deleteUrlTemplate || '');

    if (template.includes('/0/')) {
        return template.replace('/0/', `/${id}/`);
    }

    return '';
}

window.editarProduto = function editarProduto(id, nome, sku, categoria, fornecedor, estoqueAtual, quantidadeComprada, preco, precoVenda, data) {
    document.getElementById('edit_nome').value = nome;
    document.getElementById('edit_sku').value = sku || '';
    document.getElementById('edit_categoria').value = categoria || '';
    document.getElementById('edit_fornecedor').value = fornecedor;
    document.getElementById('edit_quantidade_adicionada').value = 0;
    document.getElementById('edit_quantidade_info').textContent = `Estoque atual: ${estoqueAtual || 0} • Quantidade comprada: ${quantidadeComprada || 0}`;
    document.getElementById('edit_preco').value = preco;
    document.getElementById('edit_preco_venda').value = precoVenda || '';
    document.getElementById('edit_data').value = data;

    const editUrl = resolveProdutoUrl('edit', id);
    if (!editUrl) {
        window.AppFeedback?.showToast?.('Rota de edição de produto não configurada.', { variant: 'danger' });
        return;
    }

    document.getElementById('formEditar').action = editUrl;
    const modal = new bootstrap.Modal(document.getElementById('modalEditarProduto'));
    modal.show();
};

window.abrirModalExclusao = function abrirModalExclusao(produtoId, produtoNome, estoque, precoCusto) {
    try {
        document.getElementById('modal_excluir_produto_nome').textContent = produtoNome;
        document.getElementById('modal_excluir_produto_estoque').textContent = `${estoque} unidades`;

        const valorTotal = (estoque * precoCusto).toFixed(2);
        document.getElementById('modal_excluir_produto_valor').textContent = `R$ ${valorTotal}`;
        document.getElementById('modal_excluir_produto_id').value = produtoId;

        const modal = new bootstrap.Modal(document.getElementById('modalConfirmarExclusaoProduto'));
        modal.show();
    } catch (error) {
        console.error('Erro ao abrir modal de exclusão:', error);
    }
};

window.confirmarExclusaoProduto = function confirmarExclusaoProduto() {
    const produtoId = document.getElementById('modal_excluir_produto_id').value;
    const modal = bootstrap.Modal.getInstance(document.getElementById('modalConfirmarExclusaoProduto'));

    if (modal) {
        modal.hide();
    }

    const form = document.createElement('form');
    form.method = 'POST';
    form.action = resolveProdutoUrl('delete', produtoId);
    if (!form.action) {
        window.AppFeedback?.showToast?.('Rota de exclusão de produto não configurada.', { variant: 'danger' });
        return;
    }

    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const csrfInput = document.createElement('input');
    csrfInput.type = 'hidden';
    csrfInput.name = 'csrfmiddlewaretoken';
    csrfInput.value = csrfToken;
    form.appendChild(csrfInput);

    document.body.appendChild(form);
    form.submit();
};
