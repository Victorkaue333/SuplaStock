// Preencher data de vencimento com data de hoje como padrão
document.addEventListener('DOMContentLoaded', function() {
    const dataVencimentoInput = document.querySelector('input[name="data_vencimento"]');
    if (dataVencimentoInput && !dataVencimentoInput.value) {
        const hoje = new Date();
        const ano = hoje.getFullYear();
        const mes = String(hoje.getMonth() + 1).padStart(2, '0');
        const dia = String(hoje.getDate()).padStart(2, '0');
        dataVencimentoInput.value = `${ano}-${mes}-${dia}`;
    }
});

// Validação adicional antes do envio
document.querySelector('form').addEventListener('submit', function(e) {
    const valor = parseFloat(document.querySelector('input[name="valor"]').value);
    
    if (valor <= 0 || isNaN(valor)) {
        e.preventDefault();
        alert('O valor deve ser maior que zero!');
        return false;
    }
    
    const dataVencimento = new Date(document.querySelector('input[name="data_vencimento"]').value);
    const hoje = new Date();
    hoje.setHours(0, 0, 0, 0);
    
    if (dataVencimento < hoje) {
        if (!confirm('A data de vencimento está no passado. A conta será marcada como atrasada. Deseja continuar?')) {
            e.preventDefault();
            return false;
        }
    }
});
