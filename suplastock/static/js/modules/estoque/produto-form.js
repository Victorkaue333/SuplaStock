(function () {
  const imagemInput = document.getElementById('imagemInput');
  if (imagemInput) {
    imagemInput.addEventListener('change', function (e) {
      const fileName = e.target.files[0]?.name;
      if (!fileName) return;

      const label = document.querySelector('.file-input-label div div:first-child');
      if (label) {
        label.textContent = fileName;
        label.style.color = '#667eea';
      }

      const smallEl = this.nextElementSibling;
      if (smallEl) {
        smallEl.textContent = 'Imagem selecionada: ' + fileName;
        smallEl.style.color = '#667eea';
      }
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    const precoCustoInput = document.getElementById('precoCustoInput');
    const precoVendaInput = document.getElementById('precoVendaInput');
    const produtoForm = document.querySelector('form[data-sku-preview-url]');
    const nomeInput = produtoForm?.querySelector('input[name="nome"]');
    const skuInput = produtoForm?.querySelector('input[name="sku"]');

    if (precoCustoInput && precoCustoInput.dataset.initialValue) {
      const v = parseFloat(String(precoCustoInput.dataset.initialValue).replace(',', '.'));
      if (!Number.isNaN(v)) precoCustoInput.value = v.toFixed(2);
    }

    if (precoVendaInput && precoVendaInput.dataset.initialValue) {
      const v = parseFloat(String(precoVendaInput.dataset.initialValue).replace(',', '.'));
      if (!Number.isNaN(v)) precoVendaInput.value = v.toFixed(2);
    }

    if (produtoForm && nomeInput && skuInput) {
      const skuPreviewUrl = produtoForm.dataset.skuPreviewUrl || '';
      let skuDebounceTimer = null;
      let skuRequestToken = 0;

      const fallbackSku = (nome) => {
        const base = String(nome || '')
          .toUpperCase()
          .replace(/[^A-Z0-9]/g, '')
          .slice(0, 3) || 'PRD';
        return `${base}-001`;
      };

      const atualizarSkuPreview = () => {
        const nome = String(nomeInput.value || '').trim();
        skuRequestToken += 1;
        const localToken = skuRequestToken;

        if (!nome) {
          skuInput.value = '';
          return;
        }

        if (skuDebounceTimer) {
          clearTimeout(skuDebounceTimer);
        }

        skuDebounceTimer = setTimeout(async () => {
          if (!skuPreviewUrl) {
            skuInput.value = fallbackSku(nome);
            return;
          }

          try {
            const url = new URL(skuPreviewUrl, window.location.origin);
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
              throw new Error(`Erro HTTP ${response.status}`);
            }

            const payload = await response.json();
            skuInput.value = payload?.sku || fallbackSku(nome);
          } catch (error) {
            console.warn('Falha ao gerar SKU automático:', error);
            if (localToken === skuRequestToken) {
              skuInput.value = fallbackSku(nome);
            }
          }
        }, 250);
      };

      nomeInput.addEventListener('input', atualizarSkuPreview);
      if (String(nomeInput.value || '').trim()) {
        atualizarSkuPreview();
      }
    }
  });
})();
