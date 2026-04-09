(function initVAFormatters(globalScope) {
    const currencyFormatter = new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    });

    function normalizeNumber(value) {
        if (typeof value === 'number') {
            return Number.isFinite(value) ? value : 0;
        }
        const normalized = Number(value);
        return Number.isFinite(normalized) ? normalized : 0;
    }

    function formatCurrencyBRL(value) {
        return currencyFormatter.format(normalizeNumber(value));
    }

    globalScope.VAFormatters = {
        formatCurrencyBRL,
    };
}(window));
