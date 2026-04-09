# Inventory Demand Planning

**Skill:** `@inventory-demand-planning`
**Prioridade:** ðŸ”´ **ALTA** - Curto Prazo
**Status no Projeto:** âš ï¸ **FALTANDO**

---

## ðŸ“‹ O que Ã©?:

Expertise codificada para previsÃ£o de demanda, otimizaÃ§Ã£o de estoque de seguranÃ§a, planejamento de reabastecimento e estimativa de impacto de promoÃ§Ãµes em varejo multi-localizaÃ§Ã£o.

## ðŸŽ¯ O que faz?:

- **PrevisÃ£o de Demanda:** Algoritmos de forecasting (Moving Averages, Exponential Smoothing, Machine Learning)
- **CÃ¡lculo de Safety Stock:** Estoque de seguranÃ§a baseado em variabilidade de demanda e lead time
- **AnÃ¡lise ABC/XYZ:** SegmentaÃ§Ã£o de produtos por importÃ¢ncia e previsibilidade
- **Planejamento de Reabastecimento:** Quando e quanto comprar de cada fornecedor
- **Estimativa de Lift Promocional:** Impacto de promoÃ§Ãµes nas vendas

## ðŸ’¡ Como pode ajudar o SuplaStock?

### SituaÃ§Ã£o Atual:

- Alertas bÃ¡sicos de estoque baixo (quantidade < estoque_minimo)
- Sem previsÃ£o inteligente de quando produtos vÃ£o acabar
- Reabastecimento manual baseado em "feeling"
- Sem anÃ¡lise de sazonalidade (ex: Whey vende mais em Janeiro)

### Com a Skill Implementada

```python
# Exemplo de uso no seu sistema
from inventory_demand_planning import DemandForecaster

# Analisar histÃ³rico de vendas de um produto
produto = Produto.objects.get(nome="Whey Protein 900g")
vendas_historico = Venda.objects.filter(produto=produto).last_90_days()

# Gerar previsÃ£o para prÃ³ximos 30 dias
forecast = DemandForecaster.predict(
    historico=vendas_historico,
    method='exponential_smoothing',
    periods=30
)

# Calcular estoque de seguranÃ§a ideal
safety_stock = DemandForecaster.calculate_safety_stock(
    demand_std=forecast.std_deviation,
    lead_time_days=7,  # tempo do fornecedor
    service_level=0.95  # 95% de chance de nÃ£o faltar
)

# Sugerir quantidade de compra
sugestao = {
    'quantidade_comprar': forecast.total_expected + safety_stock - produto.estoque_atual,
    'data_sugerida_pedido': forecast.data_esgotamento - timedelta(days=7),
    'confianca': forecast.confidence_interval
}
```

## ðŸ“Š MÃ©tricas que vocÃª terÃ¡

- **WMAPE (Weighted Mean Absolute Percentage Error):** PrecisÃ£o da previsÃ£o
- **Bias:** Se vocÃª tende a comprar demais ou de menos
- **Fill Rate:** % de vendas atendidas sem ruptura
- **Inventory Turnover:** Giro de estoque
- **Days of Supply:** Quantos dias o estoque atual dura

## ðŸš€ ImplementaÃ§Ã£o no SuplaStock

### 1. Nova view no Dashboard

```python
# dashboard_previsao.html
- GrÃ¡fico de forecast vs real dos Ãºltimos 3 meses
- Produtos crÃ­ticos com risco de ruptura nos prÃ³ximos 7/15/30 dias
- SugestÃµes automÃ¡ticas de pedido de compra
```

### 2. Modelo de PrevisÃ£o

```python
class PrevisaoEstoque(models.Model):
    produto = models.ForeignKey(Produto)
    data_previsao = models.DateField()
    quantidade_prevista = models.IntegerField()
    confianca_inferior = models.IntegerField()  # limite inferior
    confianca_superior = models.IntegerField()  # limite superior
    metodo_usado = models.CharField(max_length=50)
    precisao_historica = models.DecimalField()  # WMAPE
```

### 3. Comando Django para rodar diariamente

```bash
python manage.py gerar_previsoes --periodo=30
```

## ðŸŽ“ Conceitos-chave

### MÃ©todos de Forecasting

| MÃ©todo | Quando usar | Complexidade |
|--------|-------------|--------------|
| **Moving Average** | Demanda estÃ¡vel, sem sazonalidade | Baixa |
| **Exponential Smoothing** | Demanda com leve tendÃªncia | MÃ©dia |
| **Holt-Winters** | Demanda sazonal (ex: Whey mais no verÃ£o) | MÃ©dia |
| **ARIMA** | Dados complexos com mÃºltiplos padrÃµes | Alta |
| **Machine Learning** | Muitos produtos + fatores externos | Muito Alta |

### CÃ¡lculo de Safety Stock

```
SS = Z Ã— Ïƒ_d Ã— âˆš(LT + RP)

Onde:
- Z = z-score do nÃ­vel de serviÃ§o (1.65 para 95%)
- Ïƒ_d = desvio padrÃ£o da demanda
- LT = lead time do fornecedor (em perÃ­odos)
- RP = perÃ­odo de revisÃ£o (em perÃ­odos)
```

**Exemplo Real:**

- Produto: Creatina 300g
- Venda mÃ©dia: 15 unid/semana (Ïƒ = 5)
- Lead time fornecedor: 2 semanas
- NÃ­vel de serviÃ§o desejado: 95% (Z=1.65)

```

SS = 1.65 Ã— 5 Ã— âˆš(2 + 1) = 1.65 Ã— 5 Ã— 1.73 = 14 unidades
```

Significa: mantenha sempre 14 unidades de "estoque de seguranÃ§a" alÃ©m do estoque para demanda esperada.

## ðŸ“š Recursos da Skill

**Path:** `C:\Users\Victor Alves\.gemini\antigravity\skills\inventory-demand-planning\`

**Arquivos principais:**

- `SKILL.md` - DocumentaÃ§Ã£o completa
- `resources/` - Exemplos de implementaÃ§Ã£o
- `templates/` - Templates de cÃ³digo

## âš¡ PrÃ³ximos Passos

1. **Fase 1 (1-2 semanas):** Implementar previsÃ£o simples (Moving Average)
2. **Fase 2 (2-3 semanas):** Adicionar Exponential Smoothing e Safety Stock
3. **Fase 3 (1 mÃªs):** Dashboard de previsÃµes e sugestÃµes automÃ¡ticas
4. **Fase 4 (Futuro):** Machine Learning para produtos complexos

## ðŸ’° ROI Esperado

- **ReduÃ§Ã£o de Ruptura:** 30-50% menos produtos faltando
- **ReduÃ§Ã£o de Estoque Parado:** 20-30% menos capital imobilizado
- **Tempo de GestÃ£o:** 70% menos tempo planejando manualmente
- **SatisfaÃ§Ã£o Cliente:** Menos "produto em falta" = mais vendas

---

**Fonte:** `github.com/ai-evos/agent-skills`  
**Data de AdiÃ§Ã£o:** 27/02/2026  
**Risco:** Seguro
