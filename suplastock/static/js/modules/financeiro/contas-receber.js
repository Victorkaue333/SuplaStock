// ==================== ESTADO DO CARRINHO ====================
let carrinhoFiado = [];
let ultimoResultadoClientes = [];

const contasReceberConfigElement = document.getElementById('contas-receber-config');
const shouldBindEvents = (() => {
    if (window.__contasReceberBindingsInitialized) {
        return false;
    }
    window.__contasReceberBindingsInitialized = true;
    return true;
})();

const apiClientesUrl = contasReceberConfigElement ? (contasReceberConfigElement.dataset.clientesUrl || '') : '';
const apiProdutosUrl = contasReceberConfigElement ? (contasReceberConfigElement.dataset.produtosUrl || '') : '';
const apiValidarEstoqueUrl = contasReceberConfigElement ? (contasReceberConfigElement.dataset.validarEstoqueUrl || '') : '';
const clienteFiadoResumoTemplate = contasReceberConfigElement ? (contasReceberConfigElement.dataset.clienteFiadoResumoTemplate || '') : '';
const resumoCardsUrl = contasReceberConfigElement ? (contasReceberConfigElement.dataset.resumoCardsUrl || '') : '';
const receberContaUrlTemplate = contasReceberConfigElement ? (contasReceberConfigElement.dataset.receberUrlTemplate || '') : '';
const receberClienteUrlTemplate = contasReceberConfigElement ? (contasReceberConfigElement.dataset.receberClienteUrlTemplate || '') : '';
const deletarContaUrlTemplate = contasReceberConfigElement ? (contasReceberConfigElement.dataset.deletarUrlTemplate || '') : '';
const editarContaUrlTemplate = contasReceberConfigElement ? (contasReceberConfigElement.dataset.editarUrlTemplate || '') : '';
const cancelarContaUrlTemplate = contasReceberConfigElement ? (contasReceberConfigElement.dataset.cancelarUrlTemplate || '') : '';
const detalheContaUrlTemplate = contasReceberConfigElement ? (contasReceberConfigElement.dataset.detalheUrlTemplate || '') : '';

const escapeHtml = (value) => String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');

const notify = (message, variant = 'info') => {
    if (window.AppFeedback?.showToast) {
        window.AppFeedback.showToast(message, { variant });
        return;
    }
    window.alert(message);
};

const fetchJson = async (url, options = {}) => {
    const timeoutMs = options.timeoutMs ?? 8000;
    const controller = new AbortController();
    const timerId = window.setTimeout(() => controller.abort(), timeoutMs);

    try {
        const response = await fetch(url, {
            ...options,
            credentials: 'same-origin',
            headers: {
                Accept: 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
                ...(options.headers || {})
            },
            signal: controller.signal
        });

        if (!response.ok) {
            throw new Error(`Falha HTTP (${response.status})`);
        }

        const contentType = response.headers.get('content-type') || '';
        if (!contentType.toLowerCase().includes('application/json')) {
            throw new Error('Resposta inválida do servidor (esperado JSON).');
        }

        return response.json();
    } finally {
        window.clearTimeout(timerId);
    }
};

let lastNotification = { message: '', at: 0 };
const notifyOnce = (message, variant = 'info', coolDownMs = 1400) => {
    const now = Date.now();
    if (lastNotification.message === message && (now - lastNotification.at) < coolDownMs) {
        return;
    }
    lastNotification = { message, at: now };
    notify(message, variant);
};

const askConfirmation = (options) => {
    if (window.AppFeedback?.confirm) {
        return window.AppFeedback.confirm(options);
    }
    return Promise.resolve(window.confirm(options?.message || 'Deseja continuar?'));
};

const buildContaUrl = (urlTemplate, contaId) => {
    if (urlTemplate.includes('/0/')) {
        return urlTemplate.replace('/0/', `/${contaId}/`);
    }
    return '';
};

const buildClienteUrl = (urlTemplate, clienteId) => {
    if (urlTemplate.includes('/0/')) {
        return urlTemplate.replace('/0/', `/${clienteId}/`);
    }
    return '';
};

const buildClienteResumoUrl = (clienteId) => {
    if (clienteFiadoResumoTemplate.includes('/0/')) {
        return clienteFiadoResumoTemplate.replace('/0/', `/${clienteId}/`);
    }
    return '';
};

const toNumber = (value) => {
    let normalized = String(value ?? '').trim();
    if (normalized.includes(',') && normalized.includes('.')) {
        normalized = normalized.replace(/\./g, '').replace(',', '.');
    } else if (normalized.includes(',')) {
        normalized = normalized.replace(',', '.');
    }
    normalized = normalized.replace(/[^\d.-]/g, '');
    const parsed = Number.parseFloat(normalized);
    return Number.isFinite(parsed) ? parsed : 0;
};

const formatCurrencyBr = (value) => `R$ ${Number(value || 0).toFixed(2).replace('.', ',')}`;

const generateIdempotencyKey = () => {
    if (window.crypto?.randomUUID) {
        return window.crypto.randomUUID();
    }
    return `rec-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
};

const normalizeText = (value) => String(value ?? '')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .trim();

const escolherClientePorTermo = (termo, clientes = []) => {
    const termoNormalizado = normalizeText(termo);
    if (!termoNormalizado) {
        return null;
    }

    const matchExato = clientes.find((cliente) => {
        const nome = normalizeText(cliente.nome);
        const codigo = normalizeText(cliente.codigo || '');
        return (
            nome === termoNormalizado
            || codigo === termoNormalizado
            || `#${codigo}` === termoNormalizado
        );
    });
    if (matchExato) {
        return matchExato;
    }

    return clientes.length === 1 ? clientes[0] : null;
};

const selecionarClientePorTermoOuPrimeiro = (termo, clientes = []) => {
    if (!Array.isArray(clientes) || clientes.length === 0) {
        return null;
    }
    return escolherClientePorTermo(termo, clientes) || clientes[0];
};

let fiadoClienteTravado = false;

const setFiadoClienteTravado = (travado) => {
    fiadoClienteTravado = Boolean(travado);
    const buscaInput = document.getElementById('fiado_cliente_busca');
    const btnLimpar = document.querySelector('#fiado_cliente_selecionado .fiado-client-clear-btn');
    if (buscaInput) {
        buscaInput.readOnly = fiadoClienteTravado;
    }
    if (btnLimpar) {
        btnLimpar.style.display = fiadoClienteTravado ? 'none' : 'inline-flex';
    }
};

const resetResumoClienteFiado = () => {
    const card = document.getElementById('fiado_cliente_resumo_card');
    const badge = document.getElementById('fiado_cliente_resumo_badge');
    const saldo = document.getElementById('fiado_cliente_resumo_saldo');
    const recebido = document.getElementById('fiado_cliente_resumo_recebido');
    const ultimaCompra = document.getElementById('fiado_cliente_resumo_ultima_compra');
    const ultimoPagamento = document.getElementById('fiado_cliente_resumo_ultimo_pagamento');
    const hint = document.getElementById('fiado_cliente_resumo_hint');

    if (card) {
        card.style.display = 'none';
    }
    if (badge) {
        badge.textContent = '0 conta(s) ativa(s)';
    }
    if (saldo) {
        saldo.textContent = 'R$ 0,00';
    }
    if (recebido) {
        recebido.textContent = 'R$ 0,00';
    }
    if (ultimaCompra) {
        ultimaCompra.textContent = '-';
    }
    if (ultimoPagamento) {
        ultimoPagamento.textContent = '-';
    }
    if (hint) {
        hint.textContent = '';
    }
};

const renderResumoClienteFiado = (resumo, hintTexto = '') => {
    const card = document.getElementById('fiado_cliente_resumo_card');
    const badge = document.getElementById('fiado_cliente_resumo_badge');
    const saldo = document.getElementById('fiado_cliente_resumo_saldo');
    const recebido = document.getElementById('fiado_cliente_resumo_recebido');
    const ultimaCompra = document.getElementById('fiado_cliente_resumo_ultima_compra');
    const ultimoPagamento = document.getElementById('fiado_cliente_resumo_ultimo_pagamento');
    const hint = document.getElementById('fiado_cliente_resumo_hint');

    if (!card || !resumo) {
        return;
    }

    const contasAtivas = Number(resumo.contas_ativas || 0);
    const contasAtrasadas = Number(resumo.contas_atrasadas || 0);

    if (badge) {
        badge.textContent = `${contasAtivas} conta(s) ativa(s)`;
        if (contasAtrasadas > 0) {
            badge.textContent += ` • ${contasAtrasadas} atrasada(s)`;
        }
    }
    if (saldo) {
        saldo.textContent = formatCurrencyBr(toNumber(resumo.saldo_aberto));
        saldo.style.color = toNumber(resumo.saldo_aberto) > 0 ? '#DC2626' : '#059669';
    }
    if (recebido) {
        recebido.textContent = formatCurrencyBr(toNumber(resumo.total_recebido));
    }
    if (ultimaCompra) {
        ultimaCompra.textContent = resumo.ultima_compra || '-';
    }
    if (ultimoPagamento) {
        ultimoPagamento.textContent = resumo.ultimo_pagamento || '-';
    }
    if (hint) {
        hint.textContent = hintTexto || 'Ao registrar esta venda, o saldo devedor do cliente será atualizado automaticamente.';
    }
    card.style.display = 'block';
};

const carregarResumoClienteFiado = async (clienteId, hintTexto = '') => {
    if (!clienteId) {
        resetResumoClienteFiado();
        return;
    }

    const card = document.getElementById('fiado_cliente_resumo_card');
    const hint = document.getElementById('fiado_cliente_resumo_hint');
    if (card) {
        card.style.display = 'block';
    }
    if (hint) {
        hint.textContent = 'Carregando resumo do fiado...';
    }

    const url = buildClienteResumoUrl(clienteId);
    if (!url) {
        if (hint) {
            hint.textContent = 'Resumo do cliente indisponível no momento.';
        }
        return;
    }

    try {
        const data = await fetchJson(url);
        renderResumoClienteFiado(data.resumo || null, hintTexto);
    } catch (error) {
        console.error('Erro ao carregar resumo de fiado do cliente:', error);
        if (hint) {
            hint.textContent = 'Não foi possível carregar o resumo do cliente.';
        }
    }
};

const atualizarEstadoBotaoFiado = () => {
    const botao = document.getElementById('fiado_btn_submit');
    if (!botao) {
        return;
    }
    const desabilitado = botao.disabled;
    botao.classList.toggle('is-disabled', desabilitado);
    botao.setAttribute('aria-disabled', desabilitado ? 'true' : 'false');
};

const setResolvingClienteState = (enabled) => {
    const form = document.getElementById('formVendaFiada');
    if (!form) {
        return;
    }
    form.dataset.resolvendoCliente = enabled ? '1' : '0';
    const botao = document.getElementById('fiado_btn_submit');
    if (!botao) {
        return;
    }

    if (!botao.dataset.defaultLabel) {
        botao.dataset.defaultLabel = botao.innerHTML;
    }

    if (enabled) {
        botao.disabled = true;
        botao.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Validando cliente...';
        atualizarEstadoBotaoFiado();
        return;
    }

    botao.innerHTML = botao.dataset.defaultLabel;
    validarFormFiado();
};

const sincronizarPayloadFiado = () => {
    const carrinhoJsonInput = document.getElementById('carrinho_json');
    if (carrinhoJsonInput) {
        carrinhoJsonInput.value = JSON.stringify(carrinhoFiado);
    }

    const itensJsonInput = document.getElementById('fiado_itens_json');
    if (itensJsonInput) {
        itensJsonInput.value = JSON.stringify(carrinhoFiado);
    }

    const clienteIdInput = document.getElementById('fiado_cliente_id');
    const clienteIdPostInput = document.getElementById('fiado_cliente_id_post');
    if (clienteIdInput && clienteIdPostInput) {
        clienteIdPostInput.value = clienteIdInput.value || '';
    }

    const clienteNomePostInput = document.getElementById('fiado_cliente_nome_post');
    if (clienteNomePostInput) {
        const nomeSelecionado = (document.getElementById('fiado_cliente_nome_display')?.textContent || '').trim();
        const nomeDigitado = (document.getElementById('fiado_cliente_busca')?.value || '').trim();
        clienteNomePostInput.value = nomeSelecionado || nomeDigitado || '';
    }
};

// ==================== FUNÇÕES DE BUSCA DE CLIENTE ====================
let clienteSearchTimer = null;
let clienteSearchRequestId = 0;
const fiadoClienteBuscaInput = document.getElementById('fiado_cliente_busca');
const fiadoClienteResultados = document.getElementById('fiado_cliente_results');

if (shouldBindEvents && fiadoClienteBuscaInput && fiadoClienteResultados) {
    fiadoClienteBuscaInput.addEventListener('input', function() {
        if (fiadoClienteTravado) {
            return;
        }
        clearTimeout(clienteSearchTimer);
        const termo = this.value.trim();
        validarFormFiado();
        if (termo.length < 2) {
            ultimoResultadoClientes = [];
            fiadoClienteResultados.classList.remove('active');
            return;
        }
        if (!apiClientesUrl) {
            return;
        }
        clienteSearchTimer = setTimeout(() => {
            const requestId = ++clienteSearchRequestId;
            fetchJson(`${apiClientesUrl}?q=${encodeURIComponent(termo)}`)
                .then((data) => {
                    if (requestId !== clienteSearchRequestId) {
                        return;
                    }
                    ultimoResultadoClientes = Array.isArray(data.clientes) ? data.clientes : [];
                    fiadoClienteResultados.innerHTML = '';
                    if (ultimoResultadoClientes.length === 0) {
                        fiadoClienteResultados.innerHTML = '<div style="padding: 16px; text-align: center; color: #94a3b8;">Nenhum cliente encontrado</div>';
                    } else {
                        ultimoResultadoClientes.forEach((c) => {
                            const nome = escapeHtml(c.nome);
                            const codigo = c.codigo ? '#' + escapeHtml(c.codigo) : '';
                            const telefone = c.telefone ? '• ' + escapeHtml(c.telefone) : '';
                            const div = document.createElement('div');
                            div.className = 'client-result-item';
                            div.innerHTML = `
                                <div style="font-weight: 600; color: #1e293b;">${nome}</div>
                                <div style="font-size: 12px; color: #64748b;">${codigo} ${telefone}</div>
                            `;
                            div.onclick = () => selecionarClienteFiado(c);
                            fiadoClienteResultados.appendChild(div);
                        });
                    }
                    fiadoClienteResultados.classList.add('active');
                })
                .catch((error) => {
                    console.error('Erro ao buscar clientes:', error);
                });
        }, 300);
    });

    fiadoClienteBuscaInput.addEventListener('keydown', function(event) {
        if (fiadoClienteTravado) {
            return;
        }
        if (event.key !== 'Enter') {
            return;
        }
        event.preventDefault();
        const clienteEncontrado = selecionarClientePorTermoOuPrimeiro(this.value, ultimoResultadoClientes);
        if (clienteEncontrado) {
            selecionarClienteFiado(clienteEncontrado);
        } else {
            notifyOnce('Cliente não encontrado. Ao registrar, será criado automaticamente.', 'info', 3000);
        }
    });

    fiadoClienteBuscaInput.addEventListener('blur', function() {
        if (fiadoClienteTravado) {
            return;
        }
        const termo = this.value.trim();
        if (!termo || document.getElementById('fiado_cliente_id')?.value) {
            return;
        }
        window.setTimeout(() => {
            if (document.getElementById('fiado_cliente_id')?.value) {
                return;
            }
            const clienteEncontrado = escolherClientePorTermo(termo, ultimoResultadoClientes);
            if (clienteEncontrado) {
                selecionarClienteFiado(clienteEncontrado);
            }
        }, 120);
    });
}

function selecionarClienteFiado(cliente) {
    const clienteIdInput = document.getElementById('fiado_cliente_id');
    const clienteBuscaInput = document.getElementById('fiado_cliente_busca');
    const resultados = document.getElementById('fiado_cliente_results');
    const selecionadoBox = document.getElementById('fiado_cliente_selecionado');
    const nomeDisplay = document.getElementById('fiado_cliente_nome_display');
    const codigoDisplay = document.getElementById('fiado_cliente_codigo_display');

    if (!clienteIdInput || !clienteBuscaInput || !resultados || !selecionadoBox || !nomeDisplay || !codigoDisplay) {
        return;
    }

    clienteIdInput.value = cliente.id;
    clienteBuscaInput.value = cliente.nome;
    clienteBuscaInput.style.display = 'none';
    resultados.classList.remove('active');
    selecionadoBox.style.display = 'block';
    nomeDisplay.textContent = cliente.nome;
    codigoDisplay.textContent = cliente.codigo ? '#' + cliente.codigo : '';

    const origemContaInput = document.getElementById('fiado_origem_conta_id');
    const hintTexto = origemContaInput?.value
        ? 'Lançamento vinculado ao cliente selecionado a partir da tabela.'
        : '';

    void carregarResumoClienteFiado(cliente.id, hintTexto);
    sincronizarPayloadFiado();
    validarFormFiado();
}

function limparClienteFiado() {
    if (fiadoClienteTravado) {
        return;
    }

    const clienteIdInput = document.getElementById('fiado_cliente_id');
    const clienteBuscaInput = document.getElementById('fiado_cliente_busca');
    const selecionadoBox = document.getElementById('fiado_cliente_selecionado');
    const nomeDisplay = document.getElementById('fiado_cliente_nome_display');
    const codigoDisplay = document.getElementById('fiado_cliente_codigo_display');

    if (clienteIdInput) {
        clienteIdInput.value = '';
    }
    if (clienteBuscaInput) {
        clienteBuscaInput.value = '';
        clienteBuscaInput.style.display = 'block';
    }
    if (selecionadoBox) {
        selecionadoBox.style.display = 'none';
    }
    if (nomeDisplay) {
        nomeDisplay.textContent = '';
    }
    if (codigoDisplay) {
        codigoDisplay.textContent = '';
    }

    const origemContaInput = document.getElementById('fiado_origem_conta_id');
    if (origemContaInput) {
        origemContaInput.value = '';
    }

    ultimoResultadoClientes = [];
    resetResumoClienteFiado();
    sincronizarPayloadFiado();
    validarFormFiado();
}

// Fechar resultados ao clicar fora
if (shouldBindEvents) {
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.client-search-box')) {
            document.getElementById('fiado_cliente_results')?.classList.remove('active');
        }
    });
}

// ==================== SELEÇÃO DE PRODUTO (ESTILO TELA DE VENDAS) ====================
let produtoSelecionadoFiado = null;
const fiadoProdutoSelectTemp = document.getElementById('fiado_produto_select_temp');
const fiadoQuantidadeInput = document.getElementById('fiado_quantidade_input');
const fiadoPrecoUnitarioInput = document.getElementById('fiado_preco_unitario_input');
const fiadoAdicionarProdutoBtn = document.getElementById('fiado_btn_add_item');
const fiadoEstoqueWarning = document.getElementById('fiado_estoque_warning');

const formatCurrencyInput = (value) => Number(value || 0).toFixed(2).replace('.', ',');

const parseProdutoOptionFiado = (option) => {
    if (!option || !option.value) {
        return null;
    }
    return {
        id: Number.parseInt(option.value, 10),
        nome: option.dataset.nome || option.textContent || 'Produto',
        categoria: option.dataset.categoria || 'Sem categoria',
        preco_venda: Number.parseFloat(option.dataset.precoVenda) || 0,
        preco_custo: Number.parseFloat(option.dataset.precoCusto) || 0,
        estoque: Number.parseInt(option.dataset.estoque, 10) || 0
    };
};

const limparSelecaoProdutoFiado = () => {
    produtoSelecionadoFiado = null;
    if (fiadoProdutoSelectTemp) {
        fiadoProdutoSelectTemp.value = '';
    }
    if (fiadoPrecoUnitarioInput) {
        fiadoPrecoUnitarioInput.value = '0,00';
    }
    if (fiadoEstoqueWarning) {
        fiadoEstoqueWarning.textContent = '';
        fiadoEstoqueWarning.style.color = '';
    }
};

const atualizarProdutoSelecionadoFiado = () => {
    if (!fiadoProdutoSelectTemp) {
        produtoSelecionadoFiado = null;
        return;
    }

    produtoSelecionadoFiado = parseProdutoOptionFiado(fiadoProdutoSelectTemp.options[fiadoProdutoSelectTemp.selectedIndex]);
    if (!produtoSelecionadoFiado) {
        if (fiadoPrecoUnitarioInput) {
            fiadoPrecoUnitarioInput.value = '0,00';
        }
        if (fiadoEstoqueWarning) {
            fiadoEstoqueWarning.textContent = '';
        }
        return;
    }

    if (fiadoPrecoUnitarioInput) {
        fiadoPrecoUnitarioInput.value = formatCurrencyInput(produtoSelecionadoFiado.preco_venda);
    }
    if (fiadoEstoqueWarning) {
        fiadoEstoqueWarning.textContent = `Estoque disponível: ${produtoSelecionadoFiado.estoque}`;
        fiadoEstoqueWarning.style.color = produtoSelecionadoFiado.estoque > 0 ? '#0369A1' : '#DC2626';
    }
};

const adicionarProdutoSelecionadoAoCarrinho = async () => {
    atualizarProdutoSelecionadoFiado();

    if (!produtoSelecionadoFiado) {
        notify('Selecione um produto para adicionar.', 'warning');
        return;
    }

    const quantidade = Number.parseInt(fiadoQuantidadeInput?.value, 10) || 1;
    if (quantidade <= 0) {
        notify('Informe uma quantidade maior que zero.', 'warning');
        return;
    }

    await adicionarProdutoCarrinho(produtoSelecionadoFiado, quantidade);
};

if (shouldBindEvents && fiadoProdutoSelectTemp) {
    fiadoProdutoSelectTemp.addEventListener('change', atualizarProdutoSelecionadoFiado);
}

if (shouldBindEvents && fiadoAdicionarProdutoBtn) {
    fiadoAdicionarProdutoBtn.addEventListener('click', () => {
        void adicionarProdutoSelecionadoAoCarrinho();
    });
}

if (shouldBindEvents && fiadoQuantidadeInput) {
    fiadoQuantidadeInput.addEventListener('keydown', (event) => {
        if (event.key === 'Enter') {
            event.preventDefault();
            void adicionarProdutoSelecionadoAoCarrinho();
        }
    });
}

// ==================== FUNÇÕES DO CARRINHO ====================
async function validarEstoqueServidor(produtoId, quantidade) {
    if (!apiValidarEstoqueUrl) {
        return { disponivel: true };
    }
    try {
        return await fetchJson(
            `${apiValidarEstoqueUrl}?produto_id=${encodeURIComponent(produtoId)}&quantidade=${encodeURIComponent(quantidade)}`
        );
    } catch (error) {
        console.error('Falha na validação de estoque via API:', error);
        return { disponivel: true };
    }
}

async function adicionarProdutoCarrinho(produto, quantidadeAdicionar = 1) {
    const existente = carrinhoFiado.find(i => i.produto_id === produto.id);
    const estoqueProduto = Number.parseInt(produto.estoque, 10) || 0;
    const quantidadeSolicitada = Math.max(1, Number.parseInt(quantidadeAdicionar, 10) || 1);
    const quantidadeDesejada = existente ? (existente.quantidade + quantidadeSolicitada) : quantidadeSolicitada;

    const validacaoEstoque = await validarEstoqueServidor(produto.id, quantidadeDesejada);
    if (validacaoEstoque && validacaoEstoque.disponivel === false) {
        const estoqueAtual = Number.parseInt(validacaoEstoque.estoque_atual, 10);
        const estoqueValido = Number.isInteger(estoqueAtual) ? estoqueAtual : estoqueProduto;
        notify(`Estoque insuficiente. Disponível: ${estoqueValido}.`, 'warning');
        return;
    }

    if (existente) {
        if (quantidadeDesejada <= estoqueProduto) {
            existente.quantidade = quantidadeDesejada;
        } else {
            notify(`Estoque insuficiente. Disponível: ${estoqueProduto}.`, 'warning');
            return;
        }
    } else {
        carrinhoFiado.push({
            produto_id: produto.id,
            nome: produto.nome,
            categoria: produto.categoria,
            preco_unitario: parseFloat(produto.preco_venda),
            preco_custo: parseFloat(produto.preco_custo || 0),
            quantidade: quantidadeSolicitada,
            estoque: estoqueProduto
        });
    }

    if (fiadoQuantidadeInput) {
        fiadoQuantidadeInput.value = '1';
    }
    limparSelecaoProdutoFiado();
    renderizarCarrinho();
}

function removerDoCarrinho(index) {
    carrinhoFiado.splice(index, 1);
    renderizarCarrinho();
}

function alterarQuantidade(index, delta) {
    const item = carrinhoFiado[index];
    const novaQtd = item.quantidade + delta;
    if (novaQtd < 1) {
        removerDoCarrinho(index);
        return;
    }
    if (novaQtd > item.estoque) {
        notify(`Estoque insuficiente. Disponível: ${item.estoque}.`, 'warning');
        return;
    }
    item.quantidade = novaQtd;
    renderizarCarrinho();
}

function setQuantidade(index, valor) {
    const item = carrinhoFiado[index];
    const novaQtd = parseInt(valor) || 1;
    if (novaQtd < 1) {
        removerDoCarrinho(index);
        return;
    }
    if (novaQtd > item.estoque) {
        notify(`Estoque insuficiente. Disponível: ${item.estoque}.`, 'warning');
        item.quantidade = item.estoque;
    } else {
        item.quantidade = novaQtd;
    }
    renderizarCarrinho();
}

function renderizarCarrinho() {
    const container = document.getElementById('fiado_carrinho_itens');
    const vazio = document.getElementById('fiado_carrinho_vazio');
    const carrinhoSection = document.getElementById('fiado_carrinho_section');
    const resumoSection = document.getElementById('fiado_resumo_section');
    const carrinhoCountEl = document.getElementById('fiado_carrinho_count');
    const totalItensEl = document.getElementById('fiado_total_itens');
    const totalVendaEl = document.getElementById('fiado_total_venda');
    const lucroTotalEl = document.getElementById('fiado_lucro_total');
    
    if (carrinhoFiado.length === 0) {
        container.innerHTML = '';
        vazio.style.display = 'block';
        if (carrinhoSection) {
            carrinhoSection.style.display = 'none';
        }
        if (resumoSection) {
            resumoSection.style.display = 'none';
        }
        if (carrinhoCountEl) {
            carrinhoCountEl.textContent = '0';
        }
        if (totalItensEl) {
            totalItensEl.textContent = '0';
        }
        if (totalVendaEl) {
            totalVendaEl.textContent = 'R$ 0,00';
        }
        if (lucroTotalEl) {
            lucroTotalEl.textContent = 'R$ 0,00';
        }
    } else {
        vazio.style.display = 'none';
        if (carrinhoSection) {
            carrinhoSection.style.display = 'block';
        }
        if (resumoSection) {
            resumoSection.style.display = 'block';
        }
        
        let totalVenda = 0;
        let totalCusto = 0;
        let totalItens = 0;
        container.innerHTML = carrinhoFiado.map((item, index) => {
            const subtotal = item.preco_unitario * item.quantidade;
            const custoSubtotal = (item.preco_custo || 0) * item.quantidade;
            const nome = escapeHtml(item.nome);
            const categoria = escapeHtml(item.categoria);
            totalVenda += subtotal;
            totalCusto += custoSubtotal;
            totalItens += item.quantidade;
            return `
                <tr>
                    <td style="padding: 14px;">
                        <div style="font-weight: 600; color: #1e293b;">${nome}</div>
                        <div style="font-size: 12px; color: #64748b;"><i class="fas fa-tag" style="font-size: 10px;"></i> ${categoria}</div>
                    </td>
                    <td style="padding: 14px; text-align: center; font-weight: 700; color: #475569;">${item.quantidade}</td>
                    <td style="padding: 14px; text-align: right; color: #64748b;">R$ ${item.preco_unitario.toFixed(2).replace('.', ',')}</td>
                    <td style="padding: 14px; text-align: right; font-weight: 700; color: #059669;">R$ ${subtotal.toFixed(2).replace('.', ',')}</td>
                    <td style="padding: 14px; text-align: center;">
                        <button type="button" onclick="removerDoCarrinho(${index})" class="btn" style="width: 34px; height: 34px; border-radius: 10px; border: none; background: #DC2626; color: white;" aria-label="Remover ${nome} do carrinho">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                </tr>
            `;
        }).join('');

        if (carrinhoCountEl) {
            carrinhoCountEl.textContent = String(carrinhoFiado.length);
        }
        if (totalItensEl) {
            totalItensEl.textContent = String(totalItens);
        }
        if (totalVendaEl) {
            totalVendaEl.textContent = 'R$ ' + totalVenda.toFixed(2).replace('.', ',');
        }
        if (lucroTotalEl) {
            const lucro = totalVenda - totalCusto;
            lucroTotalEl.textContent = 'R$ ' + lucro.toFixed(2).replace('.', ',');
        }
    }
    
    sincronizarPayloadFiado();
    validarFormFiado();
}

function validarFormFiado() {
    const clienteIdInput = document.getElementById('fiado_cliente_id');
    const clienteBuscaInput = document.getElementById('fiado_cliente_busca');
    const temClienteSelecionado = (clienteIdInput?.value || '').trim() !== '';
    const temClienteDigitado = (clienteBuscaInput?.value || '').trim().length >= 2;
    const temItens = carrinhoFiado.length > 0;
    document.getElementById('fiado_btn_submit').disabled = !(temItens && (temClienteSelecionado || temClienteDigitado));
    atualizarEstadoBotaoFiado();
}

// ==================== SUBMIT DO FORM FIADO ====================
const formVendaFiada = document.getElementById('formVendaFiada');
if (shouldBindEvents && formVendaFiada) {
    formVendaFiada.addEventListener('submit', function(e) {
        if (this.dataset.resolvendoCliente === '1') {
            e.preventDefault();
            return false;
        }

        if (carrinhoFiado.length === 0) {
            e.preventDefault();
            notifyOnce('Adicione pelo menos um produto ao carrinho.', 'warning');
            return false;
        }

        const clienteIdInput = document.getElementById('fiado_cliente_id');
        if (!clienteIdInput.value) {
            const buscaInput = document.getElementById('fiado_cliente_busca');
            const termoCliente = (buscaInput?.value || '').trim();

            const clienteDoCache = selecionarClientePorTermoOuPrimeiro(termoCliente, ultimoResultadoClientes);
            if (clienteDoCache) {
                selecionarClienteFiado(clienteDoCache);
            }
        }

        if (!document.getElementById('fiado_cliente_id').value) {
            const buscaInput = document.getElementById('fiado_cliente_busca');
            const termoCliente = (buscaInput?.value || '').trim();

            if (!termoCliente) {
                e.preventDefault();
                notifyOnce('Informe o nome do cliente para continuar.', 'warning', 2500);
                return false;
            }

            if (!document.getElementById('fiado_cliente_id').value) {
                // Sem cadastro prévio: backend cria cliente automaticamente usando o nome digitado.
                notifyOnce('Cliente não cadastrado: será criado automaticamente ao registrar.', 'info', 3000);
            }
        }

        sincronizarPayloadFiado();
    });
}

function abrirNovoLancamentoFiado(clienteId, clienteNome, clienteCodigo = '', origemContaId = null) {
    if (!clienteId) {
        notify('Cliente inválido para novo lançamento.', 'warning');
        return;
    }

    const modalElement = document.getElementById('modalVendaFiada');
    if (!modalElement) {
        notify('Modal de venda fiada não encontrado.', 'danger');
        return;
    }

    carrinhoFiado = [];
    renderizarCarrinho();
    if (fiadoProdutoSelectTemp) {
        fiadoProdutoSelectTemp.value = '';
    }
    if (fiadoQuantidadeInput) {
        fiadoQuantidadeInput.value = '1';
    }
    limparSelecaoProdutoFiado();

    const origemContaInput = document.getElementById('fiado_origem_conta_id');
    if (origemContaInput) {
        origemContaInput.value = origemContaId ? String(origemContaId) : '';
    }

    setFiadoClienteTravado(true);
    selecionarClienteFiado({
        id: clienteId,
        nome: clienteNome || 'Cliente',
        codigo: clienteCodigo || '',
    });

    void carregarResumoClienteFiado(
        clienteId,
        `Novo lançamento no fiado para ${clienteNome || 'cliente selecionado'}.`
    );

    sincronizarPayloadFiado();
    validarFormFiado();
    bootstrap.Modal.getOrCreateInstance(modalElement).show();
}

// ==================== FUNÇÕES DOS MODAIS EXISTENTES ====================
function registrarRecebimento(contaId, clienteNome, valorSaldoAberto) {
    const saldo = toNumber(valorSaldoAberto);
    document.getElementById('modal_cliente_nome').textContent = clienteNome;
    document.getElementById('modal_valor').textContent = formatCurrencyBr(saldo);
    const valorRecebidoInput = document.getElementById('modal_valor_recebido');
    if (valorRecebidoInput) {
        valorRecebidoInput.max = saldo.toFixed(2);
        valorRecebidoInput.value = saldo.toFixed(2);
    }
    const receberUrl = buildContaUrl(receberContaUrlTemplate, contaId);
    if (!receberUrl) {
        notify('Rota de recebimento não configurada.', 'danger');
        return;
    }
    const formRecebimento = document.getElementById('formRecebimento');
    formRecebimento.action = receberUrl;
    formRecebimento.dataset.currentSaldo = saldo.toFixed(2);
    formRecebimento.dataset.submitting = '0';
    const idempotencyInput = document.getElementById('modal_idempotency_key');
    if (idempotencyInput) {
        idempotencyInput.value = generateIdempotencyKey();
    }

    const btnSubmit = document.getElementById('btn_confirmar_recebimento');
    if (btnSubmit) {
        btnSubmit.disabled = false;
        btnSubmit.innerHTML = '<i class="fas fa-check"></i> Confirmar Recebimento';
    }

    // Preencher data com hoje
    const hoje = new Date();
    const dataInput = document.querySelector('#modalRegistrarRecebimento input[name="data_recebimento"]');
    if (dataInput) {
        dataInput.value = `${hoje.getFullYear()}-${String(hoje.getMonth()+1).padStart(2,'0')}-${String(hoje.getDate()).padStart(2,'0')}`;
    }
    new bootstrap.Modal(document.getElementById('modalRegistrarRecebimento')).show();
}

function registrarRecebimentoCliente(clienteId, clienteNome, valorSaldoAberto) {
    const saldo = toNumber(valorSaldoAberto);
    document.getElementById('modal_cliente_nome').textContent = clienteNome;
    document.getElementById('modal_valor').textContent = formatCurrencyBr(saldo);

    const valorRecebidoInput = document.getElementById('modal_valor_recebido');
    if (valorRecebidoInput) {
        valorRecebidoInput.max = saldo.toFixed(2);
        valorRecebidoInput.value = saldo.toFixed(2);
    }

    const receberUrl = buildClienteUrl(receberClienteUrlTemplate, clienteId);
    if (!receberUrl) {
        notify('Rota de recebimento consolidado não configurada.', 'danger');
        return;
    }

    const formRecebimento = document.getElementById('formRecebimento');
    formRecebimento.action = receberUrl;
    formRecebimento.dataset.currentSaldo = saldo.toFixed(2);
    formRecebimento.dataset.submitting = '0';

    const idempotencyInput = document.getElementById('modal_idempotency_key');
    if (idempotencyInput) {
        idempotencyInput.value = generateIdempotencyKey();
    }

    const btnSubmit = document.getElementById('btn_confirmar_recebimento');
    if (btnSubmit) {
        btnSubmit.disabled = false;
        btnSubmit.innerHTML = '<i class="fas fa-check"></i> Confirmar Recebimento';
    }

    const hoje = new Date();
    const dataInput = document.querySelector('#modalRegistrarRecebimento input[name="data_recebimento"]');
    if (dataInput) {
        dataInput.value = `${hoje.getFullYear()}-${String(hoje.getMonth() + 1).padStart(2, '0')}-${String(hoje.getDate()).padStart(2, '0')}`;
    }
    new bootstrap.Modal(document.getElementById('modalRegistrarRecebimento')).show();
}

function excluirContaLancamento(contaId) {
    const contaNumerica = Number.parseInt(contaId, 10);
    if (!Number.isInteger(contaNumerica) || contaNumerica <= 0) {
        notify('Conta inválida para exclusão.', 'warning');
        return;
    }

    const deleteUrl = buildContaUrl(deletarContaUrlTemplate, contaNumerica);
    if (!deleteUrl) {
        notify('Rota de exclusão não configurada.', 'danger');
        return;
    }

    askConfirmation({
        title: 'Excluir lançamento do fiado',
        message: `Confirma excluir permanentemente a conta #${contaNumerica}? Esta ação remove o lançamento e pode restaurar o estoque.`,
        confirmText: 'Excluir',
        cancelText: 'Cancelar',
        variant: 'danger'
    }).then((confirmed) => {
        if (!confirmed) {
            return;
        }

        const form = document.getElementById('formDeleteContaFromModal');
        if (!form) {
            notify('Formulário de exclusão não encontrado.', 'danger');
            return;
        }

        form.action = deleteUrl;
        form.submit();
    });
}

function editarConta(contaId) {
    const editarUrl = buildContaUrl(editarContaUrlTemplate, contaId);
    if (!editarUrl) {
        notify('Rota de edição não configurada.', 'danger');
        return;
    }

    fetch(editarUrl)
        .then(r => r.json())
        .then(data => {
            document.getElementById('edit_conta_id').value = data.id;
            document.getElementById('edit_cliente').value = data.cliente_id;
            document.getElementById('edit_venda').value = data.venda_id;
            document.getElementById('edit_descricao').value = data.descricao;
            document.getElementById('edit_valor').value = data.valor;
            document.getElementById('edit_data_vencimento').value = data.data_vencimento;
            document.getElementById('edit_observacoes').value = data.observacoes;
            document.getElementById('edit_status').value = data.status;
            document.getElementById('formEditarConta').action = editarUrl;
            new bootstrap.Modal(document.getElementById('modalEditarConta')).show();
        })
        .catch(() => notify('Erro ao carregar os dados da conta.', 'danger'));
}

function cancelarConta(contaId, clienteNome) {
    document.getElementById('cancelar_cliente_nome').textContent = clienteNome;
    const cancelarUrl = buildContaUrl(cancelarContaUrlTemplate, contaId);
    if (!cancelarUrl) {
        notify('Rota de cancelamento não configurada.', 'danger');
        return;
    }
    document.getElementById('formCancelarConta').action = cancelarUrl;
    new bootstrap.Modal(document.getElementById('modalCancelarConta')).show();
}

// ==================== DETALHES DA CONTA ====================
function verDetalhes(contaId) {
    const body = document.getElementById('modalDetalhesBody');
    body.innerHTML = '<div style="text-align: center; padding: 40px;"><i class="fas fa-spinner fa-spin" style="font-size: 32px; color: #667eea;"></i></div>';
    new bootstrap.Modal(document.getElementById('modalDetalhes')).show();
    
    const detalheUrl = buildContaUrl(detalheContaUrlTemplate, contaId);
    if (!detalheUrl) {
        body.innerHTML = `<div style="text-align: center; padding: 40px; color: #DC2626;"><i class="fas fa-exclamation-circle" style="font-size: 32px;"></i><p>Rota de detalhe não configurada</p></div>`;
        notify('Rota de detalhe não configurada.', 'danger');
        return;
    }

    fetch(detalheUrl)
        .then(r => r.json())
        .then(data => {
            // Mudar cor do header se for fiado
            const header = document.getElementById('modalDetalhesHeader');
            if (data.is_fiado) {
                header.style.background = 'linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%)';
            } else {
                header.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
            }

            const clienteNome = escapeHtml(data.cliente_nome);
            const clienteCodigo = data.cliente_codigo ? '#' + escapeHtml(data.cliente_codigo) : '';
            const descricao = escapeHtml(data.descricao);
            const dataVencimento = escapeHtml(data.data_vencimento);
            const statusDisplay = escapeHtml(data.status_display);
            const criadoEm = escapeHtml(data.criado_em);
            const dataRecebimento = data.data_recebimento ? escapeHtml(data.data_recebimento) : '';
            const ultimoPagamento = data.ultimo_pagamento ? escapeHtml(data.ultimo_pagamento) : '';
            const formaPagamento = data.forma_pagamento ? escapeHtml(data.forma_pagamento) : '';
            const observacoes = data.observacoes
                ? escapeHtml(data.observacoes).replace(/\n/g, '<br>')
                : '';
            const totalItens = Number.parseInt(data.total_itens, 10) || 0;
            const totalRecebido = toNumber(data.total_recebido);
            const saldoAberto = toNumber(data.saldo_aberto);
            const totalPagamentos = Number.parseInt(data.total_pagamentos, 10) || 0;
            
            let html = `
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 24px;">
                    <div>
                        <h4 style="font-weight: 800; color: #1e293b; margin: 0;">${clienteNome}</h4>
                        <span style="color: #8B5CF6; font-size: 13px;">${clienteCodigo}</span>
                    </div>
                    <div>
                        ${data.is_fiado ? '<span class="badge-fiado"><i class="fas fa-shopping-cart"></i> VENDA FIADA</span>' : '<span class="badge-avulsa"><i class="fas fa-file-alt"></i> AVULSA</span>'}
                    </div>
                </div>
                
                <div style="background: #f8fafc; padding: 20px; border-radius: 12px; margin-bottom: 24px;">
                    <div class="detail-row"><span class="detail-label">Descrição</span><span class="detail-value">${descricao}</span></div>
                    <div class="detail-row"><span class="detail-label">Valor Total</span><span class="detail-value" style="color: #10B981; font-size: 18px;">${formatCurrencyBr(toNumber(data.valor))}</span></div>
                    <div class="detail-row"><span class="detail-label">Total Recebido</span><span class="detail-value" style="color: #0f766e;">${formatCurrencyBr(totalRecebido)}</span></div>
                    <div class="detail-row"><span class="detail-label">Saldo em Aberto</span><span class="detail-value" style="color: #1d4ed8;">${formatCurrencyBr(saldoAberto)}</span></div>
                    <div class="detail-row"><span class="detail-label">Vencimento</span><span class="detail-value">${dataVencimento}</span></div>
                    <div class="detail-row"><span class="detail-label">Status</span><span class="detail-value">${statusDisplay}</span></div>
                    <div class="detail-row"><span class="detail-label">Criado em</span><span class="detail-value">${criadoEm}</span></div>
                    <div class="detail-row"><span class="detail-label">Qtd. de Pagamentos</span><span class="detail-value">${totalPagamentos}</span></div>
                    ${ultimoPagamento ? `<div class="detail-row"><span class="detail-label">Último Pagamento</span><span class="detail-value">${ultimoPagamento}</span></div>` : ''}
                    ${dataRecebimento ? `<div class="detail-row"><span class="detail-label">Recebido em</span><span class="detail-value" style="color: #10B981;">${dataRecebimento}</span></div>` : ''}
                    ${formaPagamento ? `<div class="detail-row"><span class="detail-label">Forma de Pagamento</span><span class="detail-value">${formaPagamento}</span></div>` : ''}
                    ${observacoes ? `<div class="detail-row"><span class="detail-label">Observações</span><span class="detail-value" style="white-space: pre-line;">${observacoes}</span></div>` : ''}
                </div>
            `;
            
            // Se tem itens (venda fiada), mostrar tabela de produtos
            if (data.itens && data.itens.length > 0) {
                html += `
                    <h5 style="font-weight: 800; color: #1e293b; margin-bottom: 16px; display: flex; align-items: center; gap: 8px;">
                        <i class="fas fa-box" style="color: #8B5CF6;"></i> Produtos da Venda Fiada (${totalItens} itens)
                    </h5>
                    <div style="overflow-x: auto;">
                        <table style="width: 100%; border-collapse: collapse;">
                            <thead>
                                <tr style="background: #F5F3FF;">
                                    <th style="padding: 12px 16px; text-align: left; font-size: 12px; font-weight: 700; color: #7C3AED; text-transform: uppercase;">Produto</th>
                                    <th style="padding: 12px 16px; text-align: center; font-size: 12px; font-weight: 700; color: #7C3AED; text-transform: uppercase;">Qtd</th>
                                    <th style="padding: 12px 16px; text-align: right; font-size: 12px; font-weight: 700; color: #7C3AED; text-transform: uppercase;">Preço Un.</th>
                                    <th style="padding: 12px 16px; text-align: right; font-size: 12px; font-weight: 700; color: #7C3AED; text-transform: uppercase;">Subtotal</th>
                                </tr>
                            </thead>
                            <tbody>
                `;
                data.itens.forEach(item => {
                    const produtoNome = escapeHtml(item.produto_nome);
                    const produtoCategoria = escapeHtml(item.produto_categoria);
                    const quantidade = Number.parseInt(item.quantidade, 10) || 0;
                    html += `
                        <tr style="border-bottom: 1px solid #f1f5f9;">
                            <td style="padding: 12px 16px;">
                                <div style="font-weight: 600; color: #1e293b;">${produtoNome}</div>
                                <div style="font-size: 12px; color: #64748b;">${produtoCategoria}</div>
                            </td>
                            <td style="padding: 12px 16px; text-align: center; font-weight: 700;">${quantidade}</td>
                            <td style="padding: 12px 16px; text-align: right;">R$ ${parseFloat(item.preco_unitario).toFixed(2).replace('.', ',')}</td>
                            <td style="padding: 12px 16px; text-align: right; font-weight: 700; color: #8B5CF6;">R$ ${parseFloat(item.subtotal).toFixed(2).replace('.', ',')}</td>
                        </tr>
                    `;
                });
                html += `
                            </tbody>
                        </table>
                    </div>
                `;
            }

            if (data.recebimentos && data.recebimentos.length > 0) {
                html += `
                    <h5 style="font-weight: 800; color: #1e293b; margin: 24px 0 12px 0; display: flex; align-items: center; gap: 8px;">
                        <i class="fas fa-money-bill-wave" style="color: #059669;"></i> Histórico de Recebimentos
                    </h5>
                    <div style="background: #f8fafc; border-radius: 12px; border: 1px solid #e2e8f0; overflow: hidden;">
                `;
                data.recebimentos.forEach((rec) => {
                    const valor = formatCurrencyBr(toNumber(rec.valor));
                    const forma = escapeHtml(rec.forma_pagamento || '-');
                    const dataRec = escapeHtml(rec.data_recebimento || '-');
                    const saldoApos = formatCurrencyBr(toNumber(rec.saldo_apos));
                    const usuario = rec.usuario ? escapeHtml(rec.usuario) : '';
                    const obs = rec.observacoes ? escapeHtml(rec.observacoes) : '';
                    html += `
                        <div style="padding: 12px 14px; border-bottom: 1px solid #e2e8f0;">
                            <div style="display: flex; justify-content: space-between; gap: 10px; flex-wrap: wrap;">
                                <strong style="color: #065f46;">${valor}</strong>
                                <span style="font-size: 12px; color: #334155;">${forma} • ${dataRec}</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; gap: 10px; flex-wrap: wrap; margin-top: 4px;">
                                <span style="font-size: 12px; color: #1d4ed8;">Saldo após: ${saldoApos}</span>
                                ${usuario ? `<span style="font-size: 12px; color: #475569;">Registrado por: ${usuario}</span>` : ''}
                            </div>
                            ${obs ? `<div style="font-size: 12px; color: #64748b; margin-top: 6px;">${obs}</div>` : ''}
                        </div>
                    `;
                });
                html += '</div>';
            } else {
                html += `
                    <h5 style="font-weight: 800; color: #1e293b; margin: 24px 0 12px 0; display: flex; align-items: center; gap: 8px;">
                        <i class="fas fa-money-bill-wave" style="color: #94a3b8;"></i> Histórico de Recebimentos
                    </h5>
                    <div style="background: #f8fafc; border-radius: 12px; border: 1px solid #e2e8f0; padding: 16px; color: #64748b; font-size: 13px;">
                        Nenhum pagamento registrado até o momento.
                    </div>
                `;
            }

            const resumoClienteFiado = data.cliente_fiado || null;
            const extratoCliente = Array.isArray(data.extrato_cliente) ? data.extrato_cliente : [];
            if (resumoClienteFiado) {
                const saldoCliente = formatCurrencyBr(toNumber(resumoClienteFiado.saldo_aberto));
                const totalRecebidoCliente = formatCurrencyBr(toNumber(resumoClienteFiado.total_recebido));
                const totalOriginalCliente = formatCurrencyBr(toNumber(resumoClienteFiado.total_original));
                const contasAtivasCliente = Number(resumoClienteFiado.contas_ativas || 0);
                const contasAtrasadasCliente = Number(resumoClienteFiado.contas_atrasadas || 0);
                const ultimaCompraCliente = escapeHtml(resumoClienteFiado.ultima_compra || '-');
                const ultimoPagamentoCliente = escapeHtml(resumoClienteFiado.ultimo_pagamento || '-');

                html += `
                    <h5 style="font-weight: 800; color: #1e293b; margin: 24px 0 12px 0; display: flex; align-items: center; gap: 8px;">
                        <i class="fas fa-book" style="color: #4F46E5;"></i> Livro de Fiado do Cliente
                    </h5>
                    <div style="background: #EEF2FF; border: 1px solid #C7D2FE; border-radius: 12px; padding: 14px; margin-bottom: 12px;">
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 10px;">
                            <div style="background: #ffffff; border-radius: 10px; padding: 10px 12px;">
                                <div style="font-size: 11px; color: #64748b; text-transform: uppercase; font-weight: 700;">Saldo Atual</div>
                                <div style="font-size: 18px; font-weight: 800; color: ${toNumber(resumoClienteFiado.saldo_aberto) > 0 ? '#DC2626' : '#059669'};">${saldoCliente}</div>
                            </div>
                            <div style="background: #ffffff; border-radius: 10px; padding: 10px 12px;">
                                <div style="font-size: 11px; color: #64748b; text-transform: uppercase; font-weight: 700;">Total Compras</div>
                                <div style="font-size: 16px; font-weight: 800; color: #334155;">${totalOriginalCliente}</div>
                            </div>
                            <div style="background: #ffffff; border-radius: 10px; padding: 10px 12px;">
                                <div style="font-size: 11px; color: #64748b; text-transform: uppercase; font-weight: 700;">Total Recebido</div>
                                <div style="font-size: 16px; font-weight: 800; color: #059669;">${totalRecebidoCliente}</div>
                            </div>
                            <div style="background: #ffffff; border-radius: 10px; padding: 10px 12px;">
                                <div style="font-size: 11px; color: #64748b; text-transform: uppercase; font-weight: 700;">Contas Ativas</div>
                                <div style="font-size: 16px; font-weight: 800; color: #1D4ED8;">${contasAtivasCliente}${contasAtrasadasCliente > 0 ? ` (${contasAtrasadasCliente} atrasada(s))` : ''}</div>
                            </div>
                        </div>
                        <div style="display: flex; justify-content: space-between; gap: 8px; flex-wrap: wrap; margin-top: 10px;">
                            <small style="color: #475569;"><strong>Última compra:</strong> ${ultimaCompraCliente}</small>
                            <small style="color: #475569;"><strong>Último pagamento:</strong> ${ultimoPagamentoCliente}</small>
                        </div>
                    </div>
                `;
            }

            if (extratoCliente.length > 0) {
                html += `
                    <h5 style="font-weight: 800; color: #1e293b; margin: 0 0 12px 0; display: flex; align-items: center; gap: 8px;">
                        <i class="fas fa-stream" style="color: #2563EB;"></i> Extrato Cronológico do Fiado
                    </h5>
                    <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 12px; overflow: hidden;">
                `;

                extratoCliente.forEach((evento) => {
                    const isCompra = evento.tipo === 'compra';
                    const corTipo = isCompra ? '#7C3AED' : '#059669';
                    const labelTipo = escapeHtml(evento.tipo_display || (isCompra ? 'Compra fiado' : 'Pagamento'));
                    const dataEvento = escapeHtml(evento.data || '-');
                    const descricaoEvento = escapeHtml(evento.descricao || (isCompra ? 'Lançamento de compra fiada' : 'Recebimento registrado'));
                    const contaRef = evento.conta_id ? `Conta #${Number(evento.conta_id)}` : '-';
                    const formaPagamento = evento.forma_pagamento ? ` • ${escapeHtml(evento.forma_pagamento)}` : '';
                    const usuarioEvento = evento.usuario ? ` • ${escapeHtml(evento.usuario)}` : '';
                    const sinal = isCompra ? '+' : '-';
                    const valorEvento = `${sinal} ${formatCurrencyBr(toNumber(evento.valor))}`;
                    const saldoAposEvento = formatCurrencyBr(toNumber(evento.saldo_apos));
                    const podeExcluir = isCompra && Boolean(evento.pode_excluir) && Number(evento.conta_id) > 0;
                    const acaoExcluir = podeExcluir
                        ? `<button type="button"
                                     onclick="excluirContaLancamento(${Number(evento.conta_id)})"
                                     title="Excluir lançamento da conta #${Number(evento.conta_id)}"
                                     aria-label="Excluir lançamento da conta #${Number(evento.conta_id)}"
                                     style="border: 1px solid #fecaca; background: #fef2f2; color: #DC2626; width: 28px; height: 28px; border-radius: 8px; display: inline-flex; align-items: center; justify-content: center; cursor: pointer;">
                                <i class="fas fa-trash"></i>
                           </button>`
                        : '';

                    html += `
                        <div style="padding: 12px 14px; border-bottom: 1px solid #E2E8F0;">
                            <div style="display: flex; justify-content: space-between; gap: 10px; flex-wrap: wrap;">
                                <span style="font-size: 12px; font-weight: 700; color: ${corTipo};">${labelTipo}</span>
                                <div style="display: inline-flex; align-items: center; gap: 8px;">
                                    ${acaoExcluir}
                                    <span style="font-size: 12px; color: #64748b;">${dataEvento}</span>
                                </div>
                            </div>
                            <div style="display: flex; justify-content: space-between; gap: 10px; flex-wrap: wrap; margin-top: 4px;">
                                <strong style="color: ${corTipo};">${valorEvento}</strong>
                                <span style="font-size: 12px; color: #1D4ED8;">Saldo após: ${saldoAposEvento}</span>
                            </div>
                            <div style="font-size: 12px; color: #475569; margin-top: 4px;">
                                ${escapeHtml(contaRef)}${formaPagamento}${usuarioEvento}
                            </div>
                            <div style="font-size: 12px; color: #64748b; margin-top: 2px;">${descricaoEvento}</div>
                        </div>
                    `;
                });

                html += '</div>';
            }
            
            body.innerHTML = html;
        })
        .catch(() => {
            body.innerHTML = `<div style="text-align: center; padding: 40px; color: #DC2626;"><i class="fas fa-exclamation-circle" style="font-size: 32px;"></i><p>Erro ao carregar detalhes</p></div>`;
            notify('Erro ao carregar detalhes da conta.', 'danger');
        });
}

const buildResumoStatusBadge = (status, statusDisplay) => {
    const safeLabel = escapeHtml(statusDisplay || status || 'Indefinido');
    if (status === 'pendente') {
        return `<span class="status-badge status-pendente"><i class="fas fa-clock"></i> ${safeLabel}</span>`;
    }
    if (status === 'atrasado') {
        return `<span class="status-badge status-atrasado"><i class="fas fa-exclamation"></i> ${safeLabel}</span>`;
    }
    if (status === 'recebido') {
        return `<span class="status-badge status-recebido"><i class="fas fa-check"></i> ${safeLabel}</span>`;
    }
    if (status === 'parcial') {
        return `<span class="status-badge" style="background: #DBEAFE; color: #1E40AF;"><i class="fas fa-hand-holding-usd"></i> ${safeLabel}</span>`;
    }
    return `<span class="status-badge" style="background: #E2E8F0; color: #334155;"><i class="fas fa-circle"></i> ${safeLabel}</span>`;
};

const renderResumoCardsConteudo = (itens = []) => {
    if (!Array.isArray(itens) || itens.length === 0) {
        return `
            <div style="text-align: center; padding: 36px 20px; color: #64748b;">
                <i class="fas fa-inbox" style="font-size: 42px; margin-bottom: 10px; opacity: 0.55;"></i>
                <p style="margin: 0; font-weight: 600;">Nenhum registro encontrado para este resumo.</p>
            </div>
        `;
    }

    const cards = itens.map((item) => {
        const id = Number(item.id) || 0;
        const clienteNome = escapeHtml(item.cliente_nome || '-');
        const clienteCodigo = item.cliente_codigo ? `#${escapeHtml(item.cliente_codigo)}` : '';
        const descricao = escapeHtml(item.descricao || '-');
        const vencimento = escapeHtml(item.data_vencimento || '-');
        const valor = formatCurrencyBr(toNumber(item.valor));
        const saldo = formatCurrencyBr(toNumber(item.saldo_aberto));
        const recebido = formatCurrencyBr(toNumber(item.total_recebido));
        const origem = escapeHtml(item.origem_display || item.origem || '-');
        const statusBadge = buildResumoStatusBadge(item.status, item.status_display);

        return `
            <article class="resumo-item">
                <div class="resumo-item-header">
                    <div>
                        <p class="resumo-item-cliente">${clienteNome}</p>
                        ${clienteCodigo ? `<span class="resumo-item-codigo">${clienteCodigo}</span>` : ''}
                    </div>
                    ${statusBadge}
                </div>
                <p class="resumo-item-descricao">${descricao}</p>
                <div class="resumo-item-metas">
                    <div class="resumo-item-meta">Vencimento<br><strong>${vencimento}</strong></div>
                    <div class="resumo-item-meta">Valor<br><strong>${valor}</strong></div>
                    <div class="resumo-item-meta">Recebido<br><strong>${recebido}</strong></div>
                    <div class="resumo-item-meta">Saldo<br><strong>${saldo}</strong></div>
                    <div class="resumo-item-meta">Origem<br><strong>${origem}</strong></div>
                </div>
                <div class="resumo-item-actions">
                    <button type="button" class="btn-action btn-action-details" onclick="verDetalhes(${id})">
                        <i class="fas fa-eye"></i> Ver detalhes
                    </button>
                </div>
            </article>
        `;
    }).join('');

    return `<div class="resumo-lista">${cards}</div>`;
};

const openResumoCardsModal = async (tipo, tituloFallback = 'Resumo') => {
    const modalElement = document.getElementById('modalResumoCards');
    const tituloEl = document.getElementById('resumoCardsTitulo');
    const subtituloEl = document.getElementById('resumoCardsSubtitulo');
    const badgeEl = document.getElementById('resumoCardsBadge');
    const valorEl = document.getElementById('resumoCardsValorTotal');
    const conteudoEl = document.getElementById('resumoCardsConteudo');

    if (!modalElement || !tituloEl || !subtituloEl || !badgeEl || !valorEl || !conteudoEl) {
        return;
    }

    if (!resumoCardsUrl) {
        notify('Endpoint de resumo não configurado.', 'warning');
        return;
    }

    tituloEl.innerHTML = `<i class="fas fa-chart-pie"></i> ${escapeHtml(tituloFallback)}`;
    subtituloEl.textContent = 'Carregando registros...';
    badgeEl.textContent = '...';
    valorEl.textContent = 'R$ 0,00';
    conteudoEl.innerHTML = `
        <div style="text-align: center; padding: 32px;">
            <i class="fas fa-spinner fa-spin" style="font-size: 28px; color: #64748b;"></i>
        </div>
    `;

    bootstrap.Modal.getOrCreateInstance(modalElement).show();

    try {
        const data = await fetchJson(`${resumoCardsUrl}?tipo=${encodeURIComponent(tipo)}`);
        const titulo = data.titulo || tituloFallback;
        const subtitulo = data.subtitulo || 'Resumo de contas relacionadas.';
        const totalItens = Number(data.total_itens || 0);
        const valorTotal = formatCurrencyBr(toNumber(data.valor_total));

        tituloEl.innerHTML = `<i class="fas fa-chart-pie"></i> ${escapeHtml(titulo)}`;
        subtituloEl.textContent = subtitulo;
        badgeEl.textContent = `${totalItens} registro(s)`;
        valorEl.textContent = valorTotal;
        conteudoEl.innerHTML = renderResumoCardsConteudo(data.itens || []);
    } catch (error) {
        console.error('Erro ao carregar resumo do card:', error);
        subtituloEl.textContent = 'Falha ao carregar os registros deste resumo.';
        badgeEl.textContent = 'Erro';
        valorEl.textContent = 'R$ 0,00';
        conteudoEl.innerHTML = `
            <div style="text-align: center; padding: 36px; color: #DC2626;">
                <i class="fas fa-exclamation-circle" style="font-size: 32px; margin-bottom: 10px;"></i>
                <p style="margin: 0;">Não foi possível carregar os dados agora.</p>
            </div>
        `;
        notify('Erro ao carregar detalhes do resumo.', 'danger');
    }
};

function bindResumoCards() {
    document.querySelectorAll('.js-resumo-card').forEach((card) => {
        if (card.dataset.resumoBound === 'true') {
            return;
        }
        card.dataset.resumoBound = 'true';

        card.addEventListener('click', () => {
            const tipo = card.dataset.resumoTipo || '';
            const titulo = card.dataset.resumoTitulo || 'Resumo';
            if (!tipo) {
                return;
            }
            openResumoCardsModal(tipo, titulo);
        });
    });
}

function bindDeleteContaConfirmations() {
    document.querySelectorAll('form.js-confirm-delete-conta').forEach((form) => {
        if (form.dataset.confirmBound === 'true') {
            return;
        }
        form.dataset.confirmBound = 'true';

        form.addEventListener('submit', (event) => {
            event.preventDefault();

            const title = form.dataset.confirmTitle || 'Confirmar exclusão';
            const message = form.dataset.confirmMessage || 'Deseja realmente excluir este registro?';

            askConfirmation({
                title,
                message,
                confirmText: 'Excluir',
                cancelText: 'Cancelar',
                variant: 'danger'
            }).then((confirmed) => {
                if (confirmed) {
                    form.submit();
                }
            });
        });
    });
}

// ==================== INICIALIZAÇÕES ====================
if (shouldBindEvents) {
    document.addEventListener('DOMContentLoaded', function() {
        bindResumoCards();
        bindDeleteContaConfirmations();
        setResolvingClienteState(false);
        validarFormFiado();
        sincronizarPayloadFiado();

        const formRecebimento = document.getElementById('formRecebimento');
        if (formRecebimento) {
            formRecebimento.addEventListener('submit', (event) => {
                const btnSubmit = document.getElementById('btn_confirmar_recebimento');
                if (formRecebimento.dataset.submitting === '1') {
                    event.preventDefault();
                    return;
                }

                const saldoAtual = toNumber(formRecebimento.dataset.currentSaldo || '0');
                const valorInput = document.getElementById('modal_valor_recebido');
                const valorRecebido = toNumber(valorInput?.value || '0');
                const idempotencyInput = document.getElementById('modal_idempotency_key');

                const resetSubmittingState = () => {
                    formRecebimento.dataset.submitting = '0';
                    if (btnSubmit) {
                        btnSubmit.disabled = false;
                        btnSubmit.innerHTML = '<i class="fas fa-check"></i> Confirmar Recebimento';
                    }
                };

                if (valorRecebido <= 0) {
                    event.preventDefault();
                    notify('Informe um valor de recebimento maior que zero.', 'warning');
                    resetSubmittingState();
                    return;
                }

                if (valorRecebido - saldoAtual > 0.0001) {
                    event.preventDefault();
                    notify('Valor recebido não pode ser maior que o saldo em aberto.', 'warning');
                    resetSubmittingState();
                    return;
                }

                if (!idempotencyInput || !idempotencyInput.value) {
                    event.preventDefault();
                    notify('Não foi possível validar esta operação. Reabra o modal e tente novamente.', 'warning');
                    resetSubmittingState();
                    return;
                }

                formRecebimento.dataset.submitting = '1';
                if (btnSubmit) {
                    btnSubmit.disabled = true;
                    btnSubmit.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Registrando...';
                }
            });
        }

        // Data padrão no modal de venda fiada
        const modalVendaFiada = document.getElementById('modalVendaFiada');
        if (modalVendaFiada) {
            modalVendaFiada.addEventListener('shown.bs.modal', function() {
                const origemContaInput = document.getElementById('fiado_origem_conta_id');
                if (!origemContaInput || !origemContaInput.value) {
                    setFiadoClienteTravado(false);
                }
                const input = document.getElementById('fiado_data_vencimento');
                if (input && !input.value) {
                    const d = new Date();
                    d.setDate(d.getDate() + 30); // 30 dias como padrão
                    input.value = `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
                }
            });

            // Limpar carrinho ao fechar modal
            modalVendaFiada.addEventListener('hidden.bs.modal', function() {
                setResolvingClienteState(false);
                setFiadoClienteTravado(false);
                carrinhoFiado = [];
                renderizarCarrinho();
                const origemContaInput = document.getElementById('fiado_origem_conta_id');
                if (origemContaInput) {
                    origemContaInput.value = '';
                }
                limparClienteFiado();
                resetResumoClienteFiado();
                if (fiadoProdutoSelectTemp) {
                    fiadoProdutoSelectTemp.value = '';
                }
                if (fiadoQuantidadeInput) {
                    fiadoQuantidadeInput.value = '1';
                }
                limparSelecaoProdutoFiado();
            });
        }

        // Auto-hide mensagens
        setTimeout(function() {
            document.querySelectorAll('.alert-dismissible').forEach(function(el) {
                new bootstrap.Alert(el).close();
            });
        }, 5000);
    });
}




