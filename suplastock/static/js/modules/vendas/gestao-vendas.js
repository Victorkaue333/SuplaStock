console.log('✅ JavaScript da página de vendas carregado!');
    
    // Carrinho de compras
    let carrinho = [];

const vendasDataElement = document.getElementById('vendas-data-json');
const fiadoCardsElement = document.getElementById('fiado-cards-json');
const vendasEditConfigElement = document.getElementById('vendas-edit-config');
const vendasDeleteConfigElement = document.getElementById('vendas-delete-config');
const vendasClientesConfigElement = document.getElementById('vendas-clientes-config');
let vendasData = {};
let fiadoCardsData = {};
let vendasEditUrlTemplate = '';
let vendasDeleteUrlTemplate = '';
let vendasCsrfToken = '';
let vendasClientesApiUrl = '';
let clienteVendaResultadosCache = [];
let clienteVendaSearchTimer = null;
let clienteVendaSearchRequestId = 0;
let ultimoCampoDescontoEditado = 'valor';

if (vendasEditConfigElement) {
    vendasEditUrlTemplate = vendasEditConfigElement.dataset.editUrlTemplate || '';
}

if (vendasDeleteConfigElement) {
    vendasDeleteUrlTemplate = vendasDeleteConfigElement.dataset.deleteUrlTemplate || '';
    vendasCsrfToken = vendasDeleteConfigElement.dataset.csrfToken || '';
}

if (vendasClientesConfigElement) {
    vendasClientesApiUrl = vendasClientesConfigElement.dataset.clientesUrl || '';
}

if (vendasDataElement) {
    try {
        vendasData = JSON.parse(vendasDataElement.textContent);
    } catch (error) {
        console.error('Erro ao parsear vendas-data-json:', error);
        vendasData = {};
    }
}

if (fiadoCardsElement) {
    try {
        fiadoCardsData = JSON.parse(fiadoCardsElement.textContent);
    } catch (error) {
        console.error('Erro ao parsear fiado-cards-json:', error);
        fiadoCardsData = {};
    }
}

window.alternarGrupoCompras = function (grupoId) {
    const linhaDetalhes = document.getElementById(`grupo-detalhes-${grupoId}`);
    const botaoToggle = document.getElementById(`toggle-grupo-${grupoId}`);
    if (!linhaDetalhes) {
        return;
    }

    const estaAberto = linhaDetalhes.style.display !== 'none';
    linhaDetalhes.style.display = estaAberto ? 'none' : 'table-row';
    if (botaoToggle) {
        botaoToggle.classList.toggle('is-open', !estaAberto);
    }
};

function escapeHtml(texto) {
    return String(texto || '')
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#39;');
}

function esconderResultadosClienteVenda() {
    const resultados = document.getElementById('cliente_venda_results');
    if (!resultados) {
        return;
    }
    resultados.innerHTML = '';
    resultados.classList.remove('active');
}

function preencherClienteVenda(cliente) {
    const clienteInput = document.getElementById('cliente_venda');
    if (!clienteInput || !cliente) {
        return;
    }
    clienteInput.value = cliente.nome || '';
    esconderResultadosClienteVenda();
}

function renderResultadosClienteVenda(clientes, termo) {
    const resultados = document.getElementById('cliente_venda_results');
    if (!resultados) {
        return;
    }

    resultados.innerHTML = '';
    if (!Array.isArray(clientes) || clientes.length === 0) {
        resultados.innerHTML = `<div class="cliente-search-empty">Nenhum cliente encontrado para "${escapeHtml(termo)}".</div>`;
        resultados.classList.add('active');
        return;
    }

    clientes.forEach((cliente) => {
        const item = document.createElement('button');
        item.type = 'button';
        item.className = 'cliente-search-item';
        item.innerHTML = `
            <span class="cliente-search-nome">${escapeHtml(cliente.nome)}</span>
            <span class="cliente-search-codigo">${cliente.codigo ? `#${escapeHtml(cliente.codigo)}` : ''}</span>
        `;
        item.addEventListener('mousedown', (event) => {
            event.preventDefault();
            preencherClienteVenda(cliente);
        });
        resultados.appendChild(item);
    });
    resultados.classList.add('active');
}

function normalizarValorMonetario(valorBruto) {
    if (typeof valorBruto === 'number') {
        return Number.isFinite(valorBruto) ? valorBruto : NaN;
    }

    let texto = String(valorBruto || '').trim();
    if (!texto) {
        return NaN;
    }

    texto = texto.replace(/[^\d,.-]/g, '');

    if (texto.includes(',') && texto.includes('.')) {
        texto = texto.replace(/\./g, '').replace(',', '.');
    } else if (texto.includes(',')) {
        texto = texto.replace(',', '.');
    }

    const valor = Number.parseFloat(texto);
    return Number.isFinite(valor) ? valor : NaN;
}

function formatarValorMonetarioParaInput(valor) {
    if (!Number.isFinite(valor)) {
        return '';
    }
    return valor.toFixed(2).replace('.', ',');
}

function formatarPercentual(valor) {
    if (!Number.isFinite(valor)) {
        return '0,00';
    }
    return valor.toFixed(2).replace('.', ',');
}

function formatarMoedaBr(valor) {
    const numero = Number.isFinite(Number(valor)) ? Number(valor) : 0;
    return `R$ ${numero.toFixed(2).replace('.', ',')}`;
}

function arredondar2(valor) {
    if (!Number.isFinite(valor)) {
        return 0;
    }
    return Number((Math.round((valor + Number.EPSILON) * 100) / 100).toFixed(2));
}

function obterResumoDescontoTemporario(source = 'valor') {
    const quantidade = Number.parseInt(document.getElementById('quantidade_temp')?.value || '0', 10);
    const precoUnitario = normalizarValorMonetario(document.getElementById('preco_temp')?.value || '');
    const descontoValorInput = normalizarValorMonetario(document.getElementById('desconto_valor_temp')?.value || '');
    const descontoPercentInput = normalizarValorMonetario(document.getElementById('desconto_percentual_temp')?.value || '');

    if (!Number.isFinite(precoUnitario) || precoUnitario <= 0 || !Number.isFinite(quantidade) || quantidade <= 0) {
        return {
            subtotalOriginal: 0,
            descontoValor: 0,
            descontoPercentual: 0,
            subtotalFinal: 0,
            precoFinalUnitario: 0,
            invalido: false,
        };
    }

    const subtotalOriginal = arredondar2(precoUnitario * quantidade);
    let descontoValor = Number.isFinite(descontoValorInput) ? arredondar2(descontoValorInput) : 0;
    let descontoPercentual = Number.isFinite(descontoPercentInput) ? Number(descontoPercentInput) : 0;

    if (source === 'percentual') {
        descontoPercentual = Math.min(Math.max(descontoPercentual, 0), 100);
        descontoValor = arredondar2(subtotalOriginal * (descontoPercentual / 100));
    } else {
        descontoValor = Math.min(Math.max(descontoValor, 0), subtotalOriginal);
        descontoPercentual = subtotalOriginal > 0 ? (descontoValor / subtotalOriginal) * 100 : 0;
    }

    const subtotalFinal = arredondar2(subtotalOriginal - descontoValor);
    const precoFinalUnitario = quantidade > 0 ? arredondar2(subtotalFinal / quantidade) : 0;
    const invalido = descontoValor < 0 || descontoValor > subtotalOriginal || subtotalFinal <= 0;

    return {
        subtotalOriginal,
        descontoValor: arredondar2(descontoValor),
        descontoPercentual: Number(Math.min(Math.max(descontoPercentual, 0), 100).toFixed(4)),
        subtotalFinal,
        precoFinalUnitario,
        invalido,
    };
}

function atualizarPreviewDescontoTemp(source = null, options = {}) {
    if (source) {
        ultimoCampoDescontoEditado = source;
    }
    const { syncInputs = true } = options;
    const resumo = obterResumoDescontoTemporario(ultimoCampoDescontoEditado);
    const descontoValorInput = document.getElementById('desconto_valor_temp');
    const descontoPercentInput = document.getElementById('desconto_percentual_temp');
    const preview = document.getElementById('desconto_preview');
    const activeElement = document.activeElement;

    if (syncInputs && descontoValorInput && !(source === 'valor' && activeElement === descontoValorInput)) {
        descontoValorInput.value = formatarValorMonetarioParaInput(resumo.descontoValor);
    }
    if (syncInputs && descontoPercentInput && !(source === 'percentual' && activeElement === descontoPercentInput)) {
        descontoPercentInput.value = formatarPercentual(resumo.descontoPercentual);
    }
    if (preview) {
        preview.textContent = `Subtotal: R$ ${resumo.subtotalOriginal.toFixed(2).replace('.', ',')} | Desconto: R$ ${resumo.descontoValor.toFixed(2).replace('.', ',')} (${formatarPercentual(resumo.descontoPercentual)}%) | Total com desconto: R$ ${resumo.subtotalFinal.toFixed(2).replace('.', ',')}`;
        preview.style.color = resumo.invalido ? '#DC2626' : '#64748b';
    }
    return resumo;
}

function dataBrasileiraParaIso(dataBr) {
    if (!dataBr || !dataBr.includes('/')) {
        return '';
    }
    const partes = dataBr.split('/');
    if (partes.length !== 3) {
        return '';
    }
    const [dia, mes, ano] = partes;
    return `${ano}-${mes.padStart(2, '0')}-${dia.padStart(2, '0')}`;
}

function mostrarModalAviso(mensagem, titulo = 'Atenção') {
    const modalElement = document.getElementById('modalAvisoSistema');
    const tituloElement = document.getElementById('modalAvisoSistemaTitulo');
    const mensagemElement = document.getElementById('modalAvisoSistemaMensagem');

    if (!modalElement || !tituloElement || !mensagemElement || typeof bootstrap === 'undefined') {
        window.alert(mensagem);
        return;
    }

    tituloElement.textContent = titulo;
    mensagemElement.textContent = mensagem;

    const modal = bootstrap.Modal.getOrCreateInstance(modalElement);
    modal.show();
}

function abrirModalResumoFiado(tipoCard) {
    const payload = fiadoCardsData[tipoCard];
    if (!payload) {
        mostrarModalAviso('Não há dados disponíveis para este indicador de fiado.');
        return;
    }

    const tituloEl = document.getElementById('fiadoModalTitulo');
    const descricaoEl = document.getElementById('fiadoModalDescricao');
    const valorEl = document.getElementById('fiadoModalValor');
    const listaEl = document.getElementById('fiadoModalLista');
    const modalElement = document.getElementById('modalResumoFiadoCard');

    if (!tituloEl || !descricaoEl || !valorEl || !listaEl || !modalElement) {
        mostrarModalAviso('Estrutura do modal de fiado não encontrada na tela.');
        return;
    }

    tituloEl.textContent = payload.titulo || 'Resumo do Fiado';
    descricaoEl.textContent = payload.descricao || '';
    valorEl.textContent = payload.valor || 'R$ 0,00';
    listaEl.innerHTML = '';

    const itens = Array.isArray(payload.itens) ? payload.itens : [];
    if (!itens.length) {
        const vazio = document.createElement('div');
        vazio.className = 'fiado-modal-empty';
        vazio.textContent = payload.vazio || 'Sem dados para este indicador.';
        listaEl.appendChild(vazio);
    } else {
        itens.forEach((item) => {
            const card = document.createElement('div');
            card.className = 'fiado-modal-item';

            const header = document.createElement('div');
            header.className = 'fiado-modal-item-header';

            const titulo = document.createElement('div');
            titulo.className = 'fiado-modal-item-title';
            titulo.textContent = item.titulo || 'Sem título';

            const tag = document.createElement('span');
            tag.className = 'fiado-modal-item-tag';
            tag.textContent = item.tag || '';

            header.appendChild(titulo);
            if (tag.textContent) {
                header.appendChild(tag);
            }

            const descricao = document.createElement('div');
            descricao.className = 'fiado-modal-item-description';
            descricao.textContent = item.descricao || '-';

            const valor = document.createElement('div');
            valor.className = 'fiado-modal-item-value';
            valor.textContent = item.valor || 'R$ 0,00';

            card.appendChild(header);
            card.appendChild(descricao);
            card.appendChild(valor);
            listaEl.appendChild(card);
        });
    }

    if (typeof bootstrap === 'undefined') {
        mostrarModalAviso('Bootstrap não está disponível para abrir o modal.');
        return;
    }

    const modal = bootstrap.Modal.getOrCreateInstance(modalElement);
    modal.show();
}

window.abrirModalResumoFiado = abrirModalResumoFiado;

    // Atualizar aviso de estoque ao selecionar produto
    document.getElementById('produto_select_temp').addEventListener('change', function() {
        const option = this.options[this.selectedIndex];
        const warning = document.getElementById('estoque_warning');
        
        if (option.value) {
            const estoque = parseInt(option.dataset.estoque);
            const precoCusto = normalizarValorMonetario(option.dataset.precoCusto);
            const precoVenda = normalizarValorMonetario(option.dataset.precoVenda);
            
            // Preencher preço automaticamente com o preço de venda cadastrado
            if (Number.isFinite(precoVenda) && precoVenda > 0) {
                document.getElementById('preco_temp').value = formatarValorMonetarioParaInput(precoVenda);
            } else if (Number.isFinite(precoCusto) && precoCusto > 0) {
                // Se não tiver preço de venda cadastrado, sugere 30% de lucro
                document.getElementById('preco_temp').value = formatarValorMonetarioParaInput(precoCusto * 1.3);
            } else {
                document.getElementById('preco_temp').value = '';
            }
            
            if (estoque <= 5) {
                warning.innerHTML = `<i class="fas fa-exclamation-triangle" style="color: #DC2626;"></i> <span style="color: #DC2626; font-weight: 600;">Atenção: Apenas ${estoque} unidades em estoque!</span>`;
                warning.style.color = '#DC2626';
            } else if (estoque <= 10) {
                warning.innerHTML = `<i class="fas fa-info-circle" style="color: #F59E0B;"></i> <span style="color: #F59E0B; font-weight: 600;">Estoque: ${estoque} unidades disponíveis</span>`;
                warning.style.color = '#F59E0B';
            } else {
                warning.innerHTML = `<i class="fas fa-check-circle" style="color: #10B981;"></i> <span style="color: #10B981; font-weight: 600;">${estoque} unidades em estoque</span>`;
                warning.style.color = '#10B981';
            }
            atualizarPreviewDescontoTemp();
        } else {
            warning.innerHTML = '';
            document.getElementById('preco_temp').value = '';
            atualizarPreviewDescontoTemp();
        }
    });

    function adicionarAoCarrinho() {
        console.log('🛒 Função adicionarAoCarrinho chamada');
        
        const produtoSelect = document.getElementById('produto_select_temp');
        const quantidade = parseInt(document.getElementById('quantidade_temp').value);
        const precoUnitario = normalizarValorMonetario(document.getElementById('preco_temp').value);
        const descontoResumo = atualizarPreviewDescontoTemp();
        
        console.log('Produto:', produtoSelect.value);
        console.log('Quantidade:', quantidade);
        console.log('Preço:', precoUnitario);
        
        if (!produtoSelect.value) {
            mostrarModalAviso('Selecione um produto!');
            return;
        }
        
        if (!quantidade || quantidade <= 0) {
            mostrarModalAviso('Informe uma quantidade válida!');
            return;
        }
        
        if (!precoUnitario || precoUnitario <= 0) {
            mostrarModalAviso('Informe um preço válido!');
            return;
        }

        if (descontoResumo.descontoValor < 0 || descontoResumo.descontoValor > descontoResumo.subtotalOriginal) {
            mostrarModalAviso('O desconto informado é inválido para este item.');
            return;
        }

        if (descontoResumo.subtotalFinal <= 0) {
            mostrarModalAviso('O desconto não pode zerar o valor do item.');
            return;
        }
        
        const option = produtoSelect.options[produtoSelect.selectedIndex];
        const produtoId = option.value;
        const produtoNome = option.dataset.nome;
        const produtoCategoria = option.dataset.categoria;
        const estoque = parseInt(option.dataset.estoque);
        const precoCusto = normalizarValorMonetario(option.dataset.precoCusto);
        const precoCustoSeguro = Number.isFinite(precoCusto) ? precoCusto : 0;
        
        // Verificar estoque
        const quantidadeJaNoCarrinho = carrinho
            .filter(item => item.id === produtoId)
            .reduce((total, item) => total + item.quantidade, 0);
            
        if (quantidade + quantidadeJaNoCarrinho > estoque) {
            mostrarModalAviso(`Estoque insuficiente! Apenas ${estoque} unidades disponíveis.\nJá existem ${quantidadeJaNoCarrinho} no carrinho.`);
            return;
        }
        
        // Adicionar ao carrinho
        carrinho.push({
            id: produtoId,
            nome: produtoNome,
            categoria: produtoCategoria,
            quantidade: quantidade,
            precoUnitario: precoUnitario,
            precoOriginalUnitario: arredondar2(precoUnitario),
            precoFinalUnitario: descontoResumo.precoFinalUnitario,
            descontoValor: descontoResumo.descontoValor,
            descontoPercentual: descontoResumo.descontoPercentual,
            subtotalOriginal: descontoResumo.subtotalOriginal,
            precoCusto: precoCustoSeguro,
            subtotal: descontoResumo.subtotalFinal
        });
        
        // Limpar campos
        produtoSelect.value = '';
        document.getElementById('quantidade_temp').value = '';
        document.getElementById('preco_temp').value = '';
        document.getElementById('desconto_valor_temp').value = '';
        document.getElementById('desconto_percentual_temp').value = '';
        ultimoCampoDescontoEditado = 'valor';
        document.getElementById('estoque_warning').innerHTML = '';
        atualizarPreviewDescontoTemp();
        
        // Atualizar visualização
        atualizarCarrinho();
    }

    function atualizarCarrinho() {
        const carrinhoItems = document.getElementById('carrinho_items');
        const carrinhoSection = document.getElementById('carrinho_section');
        const resumoSection = document.getElementById('resumo_section');
        const infoAdicionais = document.getElementById('info_adicionais');
        const carrinhoVazio = document.getElementById('carrinho_vazio');
        const btnFinalizar = document.getElementById('btn_finalizar');
        const btnLimpar = document.getElementById('btn_limpar');
        
        if (carrinho.length === 0) {
            carrinhoSection.style.display = 'none';
            resumoSection.style.display = 'none';
            infoAdicionais.style.display = 'none';
            carrinhoVazio.style.display = 'block';
            btnFinalizar.style.display = 'none';
            btnLimpar.style.display = 'none';
            document.getElementById('carrinho_json').value = '[]';
            const economiaEl = document.getElementById('economia_total');
            if (economiaEl) {
                economiaEl.textContent = 'R$ 0,00';
            }
            return;
        }
        
        carrinhoSection.style.display = 'block';
        resumoSection.style.display = 'block';
        infoAdicionais.style.display = 'block';
        carrinhoVazio.style.display = 'none';
        btnFinalizar.style.display = 'inline-block';
        btnLimpar.style.display = 'inline-block';
        
        // Atualizar contagem
        document.getElementById('carrinho_count').textContent = carrinho.length;
        
        // Renderizar itens
        carrinhoItems.innerHTML = '';
        let totalItens = 0;
        let totalVenda = 0;
        let totalCusto = 0;
        let totalEconomia = 0;
        
        carrinho.forEach((item, index) => {
            totalItens += item.quantidade;
            totalVenda += item.subtotal;
            totalCusto += item.quantidade * item.precoCusto;
            totalEconomia += item.descontoValor || 0;
            
            const row = document.createElement('tr');
            const temDesconto = Number(item.descontoValor || 0) > 0;
            row.innerHTML = `
                <td style="padding: 14px; font-weight: 600; color: #1e293b;">
                    ${item.nome}
                    ${temDesconto ? '<span style="display:inline-block;margin-left:8px;padding:2px 8px;border-radius:10px;background:#DBEAFE;color:#1D4ED8;font-size:10px;font-weight:700;">Com desconto</span>' : ''}
                    <div style="font-size: 11px; color: #64748b; font-weight: 500; margin-top: 4px;">
                        <i class="fas fa-tag" style="font-size: 10px;"></i> ${item.categoria}
                    </div>
                </td>
                <td style="padding: 14px; text-align: center; color: #64748b; font-weight: 600;">${item.quantidade}</td>
                <td style="padding: 14px; text-align: right; color: #64748b;">
                    ${temDesconto ? `<span style="text-decoration: line-through; color: #94a3b8;">R$ ${item.precoOriginalUnitario.toFixed(2).replace('.', ',')}</span>` : `R$ ${item.precoOriginalUnitario.toFixed(2).replace('.', ',')}`}
                </td>
                <td style="padding: 14px; text-align: right; font-weight: 700; color: ${temDesconto ? '#DC2626' : '#64748b'};">
                    ${temDesconto ? `R$ ${item.descontoValor.toFixed(2).replace('.', ',')}` : 'R$ 0,00'}
                </td>
                <td style="padding: 14px; text-align: center; color: #64748b; font-weight: 700;">
                    ${Number(item.descontoPercentual || 0).toFixed(2).replace('.', ',')}%
                </td>
                <td style="padding: 14px; text-align: right; font-weight: 700; color: #059669;">R$ ${item.subtotal.toFixed(2).replace('.', ',')}</td>
                <td style="padding: 14px; text-align: center;">
                    <button type="button" onclick="removerDoCarrinho(${index})" class="btn btn-sm" style="background: #FEE2E2; color: #DC2626; border: none; padding: 6px 12px; border-radius: 8px; font-weight: 600;">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            `;
            carrinhoItems.appendChild(row);
        });
        
        const lucroTotal = totalVenda - totalCusto;
        
        // Atualizar resumo
        document.getElementById('total_itens').textContent = totalItens;
        document.getElementById('total_venda').textContent = `R$ ${totalVenda.toFixed(2).replace('.', ',')}`;
        const economiaEl = document.getElementById('economia_total');
        if (economiaEl) {
            economiaEl.textContent = `R$ ${totalEconomia.toFixed(2).replace('.', ',')}`;
        }
        document.getElementById('lucro_total').textContent = `R$ ${lucroTotal.toFixed(2).replace('.', ',')}`;
        
        // Atualizar campo hidden com JSON do carrinho
        document.getElementById('carrinho_json').value = JSON.stringify(carrinho);
    }

    function removerDoCarrinho(index) {
        carrinho.splice(index, 1);
        atualizarCarrinho();
    }

    function limparCarrinho() {
        if (confirm('Tem certeza que deseja limpar todo o carrinho?')) {
            carrinho = [];
            atualizarCarrinho();
        }
    }

    // Função para exibir detalhes da venda
    function verDetalhesVenda(id, produto, categoria, quantidade, precoUnit, total, cliente, codigoCliente, pagamento, data, lucro) {
        document.getElementById('detalhe_produto').textContent = produto;
        document.getElementById('detalhe_categoria').textContent = categoria;
        document.getElementById('detalhe_quantidade').textContent = quantidade;
        document.getElementById('detalhe_preco_unit').textContent = 'R$ ' + parseFloat(precoUnit).toFixed(2).replace('.', ',');
        document.getElementById('detalhe_total').textContent = 'R$ ' + parseFloat(total).toFixed(2).replace('.', ',');
        document.getElementById('detalhe_cliente').textContent = cliente;
        document.getElementById('detalhe_codigo_cliente').textContent = codigoCliente || 'Não informado';
        document.getElementById('detalhe_pagamento').textContent = pagamento;
        document.getElementById('detalhe_data').textContent = data;
        document.getElementById('detalhe_lucro').textContent = 'R$ ' + parseFloat(lucro).toFixed(2).replace('.', ',');
        
        // Abrir modal
        var modal = new bootstrap.Modal(document.getElementById('modalDetalhesVenda'));
        modal.show();
    }

    // Definir data atual como padrão
    document.addEventListener('DOMContentLoaded', function() {
        const precoInput = document.getElementById('preco_temp');
        const quantidadeInput = document.getElementById('quantidade_temp');
        const descontoValorInput = document.getElementById('desconto_valor_temp');
        const descontoPercentInput = document.getElementById('desconto_percentual_temp');
        const today = new Date().toISOString().split('T')[0];
        const dataInput = document.getElementById('data_venda');
        const formRegistrarVenda = document.getElementById('formRegistrarVenda');
        const clienteInput = document.getElementById('cliente_venda');

        if (precoInput) {
            precoInput.addEventListener('blur', function () {
                const valor = normalizarValorMonetario(this.value);
                if (Number.isFinite(valor) && valor >= 0) {
                    this.value = formatarValorMonetarioParaInput(valor);
                }
                atualizarPreviewDescontoTemp();
            });
            precoInput.addEventListener('input', function () {
                atualizarPreviewDescontoTemp();
            });
        }

        if (quantidadeInput) {
            quantidadeInput.addEventListener('input', function () {
                atualizarPreviewDescontoTemp();
            });
        }

        if (descontoValorInput) {
            descontoValorInput.addEventListener('input', function () {
                atualizarPreviewDescontoTemp('valor', { syncInputs: true });
            });
            descontoValorInput.addEventListener('blur', function () {
                const valor = normalizarValorMonetario(this.value);
                this.value = formatarValorMonetarioParaInput(Number.isFinite(valor) ? Math.max(valor, 0) : 0);
                atualizarPreviewDescontoTemp('valor');
            });
        }

        if (descontoPercentInput) {
            descontoPercentInput.addEventListener('input', function () {
                atualizarPreviewDescontoTemp('percentual', { syncInputs: true });
            });
            descontoPercentInput.addEventListener('blur', function () {
                const valor = normalizarValorMonetario(this.value || '');
                const percentual = Number.isFinite(valor) ? Math.min(Math.max(valor, 0), 100) : 0;
                this.value = formatarPercentual(percentual);
                atualizarPreviewDescontoTemp('percentual');
            });
        }

        if (dataInput) {
            dataInput.value = today;
        }

        if (formRegistrarVenda && clienteInput) {
            // Regra principal: não permitir finalizar venda sem cliente informado.
            formRegistrarVenda.addEventListener('submit', function (event) {
                const clienteNome = (clienteInput.value || '').trim();
                if (!clienteNome) {
                    event.preventDefault();
                    clienteInput.focus();
                    mostrarModalAviso('Informe o nome do cliente para finalizar a venda.');
                }
            });
        }

        if (clienteInput) {
            clienteInput.addEventListener('input', function () {
                const termo = (this.value || '').trim();
                clearTimeout(clienteVendaSearchTimer);
                clienteVendaResultadosCache = [];
                if (termo.length < 2 || !vendasClientesApiUrl) {
                    esconderResultadosClienteVenda();
                    return;
                }

                clienteVendaSearchTimer = setTimeout(() => {
                    const requestId = ++clienteVendaSearchRequestId;
                    fetch(`${vendasClientesApiUrl}?q=${encodeURIComponent(termo)}`)
                        .then((response) => {
                            if (!response.ok) {
                                throw new Error(`HTTP ${response.status}`);
                            }
                            return response.json();
                        })
                        .then((data) => {
                            if (requestId !== clienteVendaSearchRequestId) {
                                return;
                            }
                            clienteVendaResultadosCache = Array.isArray(data.clientes) ? data.clientes : [];
                            renderResultadosClienteVenda(clienteVendaResultadosCache, termo);
                        })
                        .catch(() => {
                            if (requestId !== clienteVendaSearchRequestId) {
                                return;
                            }
                            esconderResultadosClienteVenda();
                        });
                }, 220);
            });

            clienteInput.addEventListener('keydown', function (event) {
                if (event.key !== 'Enter') {
                    return;
                }
                const resultados = document.getElementById('cliente_venda_results');
                const aberto = resultados && resultados.classList.contains('active');
                if (!aberto) {
                    return;
                }
                const clienteSelecionado = clienteVendaResultadosCache[0];
                if (!clienteSelecionado) {
                    return;
                }
                event.preventDefault();
                preencherClienteVenda(clienteSelecionado);
            });

            clienteInput.addEventListener('blur', function () {
                setTimeout(() => {
                    esconderResultadosClienteVenda();
                }, 180);
            });
        }

        document.addEventListener('click', function (event) {
            const alvo = event.target;
            if (
                alvo instanceof Element &&
                (alvo.closest('.cliente-autocomplete') || alvo.closest('#cliente_venda_results'))
            ) {
                return;
            }
            esconderResultadosClienteVenda();
        });

        const fiadoCards = document.querySelectorAll('[data-fiado-card]');
        fiadoCards.forEach((card) => {
            card.addEventListener('click', () => {
                const tipoCard = card.dataset.fiadoCard || '';
                abrirModalResumoFiado(tipoCard);
            });
        });
        
        // Resetar carrinho ao abrir modal
        const modal = document.getElementById('modalRegistrarVenda');
        modal.addEventListener('show.bs.modal', function () {
            carrinho = [];
            atualizarCarrinho();
            document.getElementById('produto_select_temp').value = '';
            document.getElementById('quantidade_temp').value = '';
            document.getElementById('preco_temp').value = '';
            document.getElementById('desconto_valor_temp').value = '';
            document.getElementById('desconto_percentual_temp').value = '';
            document.getElementById('estoque_warning').innerHTML = '';
            esconderResultadosClienteVenda();
            clienteVendaResultadosCache = [];
            ultimoCampoDescontoEditado = 'valor';
            atualizarPreviewDescontoTemp();
        });
    });

    // Dados das vendas agrupadas (JSON)
    console.log('Vendas carregadas:', vendasData);

// Teste se a função está acessível globalmente
    window.abrirModalEdicaoTransacao = function(transacaoId) {
        const venda = vendasData[transacaoId];
        if (!venda) {
            mostrarModalAviso('Dados da venda não encontrados para edição.');
            return;
        }

        if (!vendasEditUrlTemplate) {
            mostrarModalAviso('Configuração de edição não encontrada. Atualize a página e tente novamente.');
            return;
        }

        const formEditar = document.getElementById('formEditarVenda');
        const inputData = document.getElementById('editar_data_venda');
        const inputPagamento = document.getElementById('editar_forma_pagamento');
        const inputCliente = document.getElementById('editar_cliente');
        const inputTransacao = document.getElementById('editar_transacao_id');
        const produtosInfo = document.getElementById('editar_produtos_info');

        if (!formEditar || !inputData || !inputPagamento || !inputCliente || !inputTransacao || !produtosInfo) {
            mostrarModalAviso('Campos de edição não encontrados na tela.');
            return;
        }

        const dataIso = venda.dataIso || dataBrasileiraParaIso(venda.data);
        inputData.value = dataIso;

        const pagamentoAtual = venda.pagamento || 'Pago';
        const pagamentoDisponivel = Array.from(inputPagamento.options).some((opt) => opt.value === pagamentoAtual);
        inputPagamento.value = pagamentoDisponivel ? pagamentoAtual : 'Pago';

        inputCliente.value = venda.cliente && venda.cliente !== 'Não informado' ? venda.cliente : '';
        inputTransacao.value = transacaoId;
        produtosInfo.textContent = (venda.produtos || [])
            .map((produto) => `${produto.nome} (${produto.quantidade}x)`)
            .join(', ') || 'Sem produtos na transação';

        formEditar.action = vendasEditUrlTemplate.replace('TRANSACAO_ID_PLACEHOLDER', transacaoId);

        const modalElement = document.getElementById('modalEditarVenda');
        const modal = bootstrap.Modal.getOrCreateInstance(modalElement);
        modal.show();
    }

    window.verDetalhesVendaAgrupada = function(transacaoId, numProdutos) {
        console.log('🔍 Abrindo detalhes da transação:', transacaoId);
        console.log('📊 Dados disponíveis:', vendasData);
        
        const venda = vendasData[transacaoId];
        if (!venda) {
            console.error('❌ Venda não encontrada:', transacaoId);
            console.error('Transações disponíveis:', Object.keys(vendasData));
            mostrarModalAviso('Dados da venda não encontrados!');
            return;
        }

        console.log('✅ Dados da venda encontrados:', venda);

        try {
            // Preencher dados gerais
            const elementoData = document.getElementById('detalhe_data');
            const elementoCliente = document.getElementById('detalhe_cliente');
            const elementoCodigo = document.getElementById('detalhe_codigo_cliente');
            const elementoPagamento = document.getElementById('detalhe_pagamento');
            const elementoTotal = document.getElementById('detalhe_total');
            const elementoLucro = document.getElementById('detalhe_lucro');

            console.log('Verificando elementos do DOM...');
            console.log('elementoData:', elementoData);
            console.log('elementoCliente:', elementoCliente);

            if (!elementoData) {
                console.error('❌ Elemento detalhe_data não encontrado!');
                mostrarModalAviso('Erro: Modal incompleto. Verifique o console.');
                return;
            }

            elementoData.textContent = venda.data;
            elementoCliente.textContent = venda.cliente;
            elementoCodigo.textContent = venda.codigo || '—';
            elementoPagamento.textContent = venda.pagamento;
            elementoTotal.textContent = `R$ ${venda.total.toFixed(2)}`;
            elementoLucro.textContent = `R$ ${venda.lucro.toFixed(2)}`;

            // Montar lista de produtos
            let produtosHtml = '';
            venda.produtos.forEach((produto, index) => {
                const categoria = (produto.categoria || '').trim() || 'Categoria não cadastrada';
                const precoOriginalUnitario = Number(produto.precoOriginalUnitario || produto.precoUnitario || 0);
                const precoFinalUnitario = Number(produto.precoUnitario || 0);
                const subtotalOriginal = Number(produto.subtotalOriginal || (precoOriginalUnitario * Number(produto.quantidade || 0)));
                const subtotalFinal = Number(produto.subtotal || 0);
                const descontoValor = Number(produto.descontoValor || 0);
                const descontoPercentual = Number(produto.descontoPercentual || 0);
                const teveDesconto = descontoValor > 0.0001;

                produtosHtml += `
                    <div style="background: #f8f9fa; padding: 16px; border-radius: 12px; margin-bottom: ${index < venda.produtos.length - 1 ? '12px' : '0'};">
                        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 12px;">
                            <div>
                                <div style="font-weight: 700; color: #1e293b; font-size: 15px; margin-bottom: 6px;">
                                    ${produto.nome}
                                    ${teveDesconto ? '<span style="display:inline-block;margin-left:8px;padding:2px 8px;border-radius:10px;background:#DBEAFE;color:#1D4ED8;font-size:10px;font-weight:700;">Com desconto</span>' : ''}
                                </div>
                                <div style="font-size: 12px; color: #64748b;">
                                    <i class="fas fa-tag" style="margin-right: 4px;"></i> ${categoria}
                                </div>
                                <div style="font-size: 12px; color: #64748b; margin-top: 4px;">
                                    <i class="fas fa-hashtag" style="margin-right: 4px;"></i> Produto ID: ${produto.produtoId || '-'}
                                </div>
                            </div>
                            <div style="text-align: right;">
                                <div style="font-size: 13px; color: #64748b; margin-bottom: 4px;">
                                    ${produto.quantidade}x ${teveDesconto ? `<span style="text-decoration: line-through; color: #94a3b8;">${formatarMoedaBr(precoOriginalUnitario)}</span> → ` : ''}${formatarMoedaBr(precoFinalUnitario)}
                                </div>
                                <div style="font-size: 16px; font-weight: 700; color: #667eea;">
                                    ${formatarMoedaBr(subtotalFinal)}
                                </div>
                            </div>
                        </div>
                        <div style="display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; font-size: 12px;">
                            <div style="background: #fff; border: 1px solid #E2E8F0; border-radius: 8px; padding: 8px 10px;">
                                <strong style="display:block; color:#334155;">Subtotal Original</strong>
                                <span style="color:#64748b;">${formatarMoedaBr(subtotalOriginal)}</span>
                            </div>
                            <div style="background: #fff; border: 1px solid #E2E8F0; border-radius: 8px; padding: 8px 10px;">
                                <strong style="display:block; color:#334155;">Subtotal Final</strong>
                                <span style="color:#0F766E; font-weight:700;">${formatarMoedaBr(subtotalFinal)}</span>
                            </div>
                            <div style="background: #fff; border: 1px solid #E2E8F0; border-radius: 8px; padding: 8px 10px;">
                                <strong style="display:block; color:#334155;">Desconto (R$)</strong>
                                <span style="color:${teveDesconto ? '#DC2626' : '#64748b'}; font-weight:${teveDesconto ? '700' : '500'};">${formatarMoedaBr(descontoValor)}</span>
                            </div>
                            <div style="background: #fff; border: 1px solid #E2E8F0; border-radius: 8px; padding: 8px 10px;">
                                <strong style="display:block; color:#334155;">Desconto (%)</strong>
                                <span style="color:${teveDesconto ? '#DC2626' : '#64748b'}; font-weight:${teveDesconto ? '700' : '500'};">${formatarPercentual(descontoPercentual)}%</span>
                            </div>
                        </div>
                    </div>
                `;
            });

            // Atualizar campo de produto (agora mostra lista)
            document.getElementById('detalhe_produto').innerHTML = produtosHtml;
            
            // Limpar campos individuais (não usados mais)
            document.getElementById('detalhe_categoria').textContent = `${venda.produtos.length} produto(s)`;
            document.getElementById('detalhe_quantidade').textContent = venda.produtos.reduce((sum, p) => sum + p.quantidade, 0);

            console.log('✅ Dados preenchidos. Abrindo modal...');

            // Verificar se Bootstrap está disponível
            if (typeof bootstrap === 'undefined') {
                console.error('❌ Bootstrap não encontrado!');
                mostrarModalAviso('Erro: Bootstrap não carregado. Atualize a página.');
                return;
            }

            // Abrir modal
            const modalElement = document.getElementById('modalDetalhesVenda');
            if (!modalElement) {
                console.error('❌ Modal modalDetalhesVenda não encontrado!');
                mostrarModalAviso('Erro: Modal não existe no DOM.');
                return;
            }

            const modal = new bootstrap.Modal(modalElement);
            modal.show();
            console.log('✅ Modal aberto!');

        } catch (error) {
            console.error('❌ Erro ao abrir modal:', error);
            mostrarModalAviso('Erro ao abrir detalhes: ' + error.message);
        }
    }

    // Função para deletar transação completa
    window.deletarTransacao = function(transacaoId) {
        console.log('🗑️ Abrindo modal de exclusão para:', transacaoId);
        
        const venda = vendasData[transacaoId];
        if (!venda) {
            mostrarModalAviso('Dados da venda não encontrados!');
            return;
        }

        // Preencher dados no modal
        document.getElementById('modal_excluir_data').textContent = venda.data;
        document.getElementById('modal_excluir_total').textContent = `R$ ${venda.total.toFixed(2)}`;
        
        // Montar lista de produtos
        const produtosTexto = venda.produtos.map(p => `${p.nome} (${p.quantidade}x)`).join(', ');
        document.getElementById('modal_excluir_produtos').textContent = produtosTexto;
        document.getElementById('modal_excluir_total_produtos').textContent = `${venda.produtos.length} produto(s)`;
        
        // Guardar ID da transação para usar na confirmação
        document.getElementById('modal_excluir_transacao_id').value = transacaoId;

        // Abrir modal
        const modal = new bootstrap.Modal(document.getElementById('modalConfirmarExclusao'));
        modal.show();
    }

    // Função para confirmar a exclusão
    window.confirmarExclusao = function() {
        const transacaoId = document.getElementById('modal_excluir_transacao_id').value;
        console.log('✅ Confirmando exclusão de:', transacaoId);

        // Fechar modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('modalConfirmarExclusao'));
        modal.hide();

        // Criar formulário temporário
        const form = document.createElement('form');
        form.method = 'POST';
        if (!vendasDeleteUrlTemplate || !vendasCsrfToken) {
            mostrarModalAviso('Configuração de exclusão não encontrada. Atualize a página e tente novamente.');
            return;
        }
        form.action = vendasDeleteUrlTemplate.replace('TRANSACAO_ID_PLACEHOLDER', transacaoId);
        
        const csrfInput = document.createElement('input');
        csrfInput.type = 'hidden';
        csrfInput.name = 'csrfmiddlewaretoken';
        csrfInput.value = vendasCsrfToken;
        form.appendChild(csrfInput);
        
        document.body.appendChild(form);
        form.submit();
    }

