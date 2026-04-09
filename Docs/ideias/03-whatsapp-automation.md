# WhatsApp Automation

**Skill:** `@whatsapp-automation`
**Prioridade:** ðŸ”´ **ALTA** - Curto Prazo
**Status no Projeto:** âŒ **NÃƒO IMPLEMENTADO**

---

## ðŸ“‹ O que Ã©?

AutomaÃ§Ã£o especializada para envio de mensagens, notificaÃ§Ãµes e lembretes via WhatsApp Business API ou bibliotecas de automaÃ§Ã£o.

## ðŸŽ¯ O que faz?

- **Envio de Mensagens Programadas:** Lembretes de pagamento, promoÃ§Ãµes
- **NotificaÃ§Ãµes Transacionais:** ConfirmaÃ§Ã£o de venda, nota de compra
- **Templates de Mensagem:** Mensagens prÃ©-formatadas
- **Respostas AutomÃ¡ticas:** FAQ bÃ¡sico via chatbot
- **IntegraÃ§Ã£o com CRM:** HistÃ³rico de conversas vinculado ao cliente

## ðŸ’¡ Como pode ajudar o SuplaStock?

### CenÃ¡rios de Uso Perfeitos para Seu NegÃ³cio

#### 1. **CobranÃ§a de Vendas Fiadas** ðŸ”¥

```python
# Envio automÃ¡tico de lembretes de pagamento
from whatsapp_automation import WhatsAppClient

def enviar_lembrete_pagamento(conta_receber):
    cliente = conta_receber.cliente
    
    mensagem = f"""
ðŸ‹ï¸ *SuplaStock*

OlÃ¡ {cliente.nome}! ðŸ‘‹

Lembrete: VocÃª tem uma conta em aberto no valor de *R$ {conta_receber.valor_restante}*.

ðŸ“… Vencimento: {conta_receber.data_vencimento.strftime('%d/%m/%Y')}

Para pagar, entre em contato conosco ou passe na loja.

_Mensagem automÃ¡tica do sistema SuplaStock_
"""
    
    WhatsAppClient.send_message(
        phone=cliente.telefone,
        message=mensagem
    )
```

**Quando enviar:**

- 3 dias antes do vencimento
- No dia do vencimento
- 1 dia apÃ³s vencimento
- 7 dias apÃ³s vencimento (cobranÃ§a mais firme)

#### 2. **ConfirmaÃ§Ã£o de Venda**

```python
def confirmar_venda_whatsapp(venda):
    produtos = Venda.objects.filter(transacao_id=venda.transacao_id)
    lista_produtos = "\n".join([
        f"â€¢ {v.produto.nome} - {v.quantidade_vendida}x - R$ {v.valor_total}"
        for v in produtos
    ])
    
    mensagem = f"""
âœ… *Venda Confirmada!*

Obrigado pela compra, {venda.cliente.nome}!

ðŸ“¦ *Seus produtos:*
{lista_produtos}

ðŸ’° *Total:* R$ {sum(p.valor_total for p in produtos)}
ðŸ’³ *Forma de pgto:* {venda.forma_pagamento}

Volte sempre! ðŸ’ª
"""
    
    WhatsAppClient.send_message(venda.cliente.telefone, mensagem)
```

#### 3. **Alerta de Produto em Falta**

```python
# Notificar cliente quando produto voltar ao estoque
class AlertaEstoqueCliente(models.Model):
    cliente = models.ForeignKey(Cliente)
    produto = models.ForeignKey(Produto)
    notificado = models.BooleanField(default=False)

def notificar_produto_disponivel(produto):
    alertas = AlertaEstoqueCliente.objects.filter(
        produto=produto,
        notificado=False
    )
    
    for alerta in alertas:
        mensagem = f"""
ðŸŽ‰ *Produto DisponÃ­vel!*

{alerta.cliente.nome}, o produto *{produto.nome}* que vocÃª procurava estÃ¡ de volta em estoque!

ðŸ’° PreÃ§o: R$ {produto.preco_venda}
ðŸ“¦ Estoque: {produto.estoque_atual} unidades

Envie "RESERVAR" para garantir o seu!
"""
        
        WhatsAppClient.send_message(alerta.cliente.telefone, mensagem)
        alerta.notificado = True
        alerta.save()
```

#### 4. **PromoÃ§Ãµes e Marketing**

```python
# Enviar promoÃ§Ã£o para clientes ativos
def enviar_promocao_segmentada():
    # Clientes que compraram nos Ãºltimos 30 dias
    clientes_ativos = Cliente.objects.filter(
        venda__data_venda__gte=timezone.now() - timedelta(days=30)
    ).distinct()
    
    mensagem = """
ðŸ”¥ *PROMOÃ‡ÃƒO ESPECIAL*

Whey Protein 900g
De: R$ 89,90
Por: R$ 69,90 atÃ© Domingo! ðŸ’ª

SÃ³ na SuplaStock!
Corre que estÃ¡ acabando! âš¡
"""
    
    for cliente in clientes_ativos:
        WhatsAppClient.send_message(cliente.telefone, mensagem)
        time.sleep(2)  # Evitar ban por spam
```

## ðŸ”§ ImplementaÃ§Ã£o TÃ©cnica

### OpÃ§Ã£o 1: WhatsApp Business API (Oficial)

**PrÃ³s:**

- Oficial Meta/WhatsApp
- ConfiÃ¡vel e estÃ¡vel
- Templates aprovados
- Suporte oficial

**Contras:**

- Custo: ~R$ 0,05-0,15/mensagem
- Processo de aprovaÃ§Ã£o
- Requer empresa registrada

```python
# requirements.txt
twilio  # Fornece WhatsApp Business API

# settings.py
TWILIO_ACCOUNT_SID = config('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = config('TWILIO_AUTH_TOKEN')
TWILIO_WHATSAPP_NUMBER = 'whatsapp:+14155238886'

# whatsapp_client.py
from twilio.rest import Client

class WhatsAppClient:
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    
    @staticmethod
    def send_message(to_phone, message):
        message = client.messages.create(
            from_=f'whatsapp:{TWILIO_WHATSAPP_NUMBER}',
            body=message,
            to=f'whatsapp:+55{to_phone}'
        )
        return message.sid
```

### OpÃ§Ã£o 2: Baileys/WWEBJS (NÃ£o Oficial)

**PrÃ³s:**

- Gratuito
- Mais flexÃ­vel
- Sem aprovaÃ§Ã£o necessÃ¡ria

**Contras:**

- NÃ£o oficial (risco de ban)
- Menos estÃ¡vel
- Problemas com atualizaÃ§Ãµes do WhatsApp

```python
# Usar API Node.js separada com whatsapp-web.js
# Fazer chamadas HTTP do Django para Node

# whatsapp_api/index.js (Node.js)
const { Client } = require('whatsapp-web.js');
const client = new Client();

client.on('ready', () => {
    console.log('WhatsApp ready!');
});

// Endpoint para Django chamar
app.post('/send-message', (req, res) => {
    const { phone, message } = req.body;
    client.sendMessage(`55${phone}@c.us`, message);
    res.json({ success: true });
});
```

**Django integraÃ§Ã£o:**

```python
# suplastock/utils/whatsapp.py
import requests

class WhatsAppClient:
    BASE_URL = 'http://localhost:3000'
    
    @staticmethod
    def send_message(phone, message):
        response = requests.post(
            f'{WhatsAppClient.BASE_URL}/send-message',
            json={'phone': phone, 'message': message}
        )
        return response.json()
```

## ðŸ¤– Sistema de Lembretes AutomÃ¡tico

```python
# financeiro/tasks.py
from celery import shared_task
from datetime import timedelta

@shared_task
def enviar_lembretes_cobranca_diarios():
    """Roda todo dia Ã s 9h"""
    hoje = timezone.now().date()
    
    # 3 dias antes do vencimento
    contas_aviso_3d = ContaReceber.objects.filter(
        data_vencimento=hoje + timedelta(days=3),
        status='PENDENTE'
    )
    for conta in contas_aviso_3d:
        enviar_lembrete_pagamento(conta, tipo='aviso_previo')
    
    # Vence hoje
    contas_vence_hoje = ContaReceber.objects.filter(
        data_vencimento=hoje,
        status='PENDENTE'
    )
    for conta in contas_vence_hoje:
        enviar_lembrete_pagamento(conta, tipo='vencimento_hoje')
    
    # 1 dia atrasado
    contas_atrasadas_1d = ContaReceber.objects.filter(
        data_vencimento=hoje - timedelta(days=1),
        status='PENDENTE'
    )
    for conta in contas_atrasadas_1d:
        enviar_lembrete_pagamento(conta, tipo='atraso_1d')
    
    # 7 dias atrasado
    contas_atrasadas_7d = ContaReceber.objects.filter(
        data_vencimento=hoje - timedelta(days=7),
        status='PENDENTE'
    )
    for conta in contas_atrasadas_7d:
        enviar_lembrete_pagamento(conta, tipo='atraso_7d')
```

**Configurar Celery:**

```python
# suplastock/celery.py
from celery import Celery
from celery.schedules import crontab

app = Celery('suplastock')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.beat_schedule = {
    'lembretes-cobranca': {
        'task': 'financeiro.tasks.enviar_lembretes_cobranca_diarios',
        'schedule': crontab(hour=9, minute=0),  # 9h da manhÃ£
    },
}
```

## ðŸ“Š Dashboard de Mensagens

```python
# Novo modelo para tracking
class MensagemWhatsApp(models.Model):
    cliente = models.ForeignKey(Cliente)
    tipo = models.CharField(max_length=50)  # 'cobranca', 'confirmacao', 'marketing'
    mensagem = models.TextField()
    data_envio = models.DateTimeField(auto_now_add=True)
    entregue = models.BooleanField(default=False)
    lida = models.BooleanField(default=False)
    respondida = models.BooleanField(default=False)
    
    class Meta:
        verbose_name_plural = 'Mensagens WhatsApp'
```

**View de relatÃ³rio:**

```python
def relatorio_whatsapp(request):
    stats = {
        'total_enviadas': MensagemWhatsApp.objects.count(),
        'taxa_entrega': MensagemWhatsApp.objects.filter(entregue=True).count(),
        'taxa_leitura': MensagemWhatsApp.objects.filter(lida=True).count(),
        'mensagens_por_tipo': MensagemWhatsApp.objects.values('tipo').annotate(count=Count('id'))
    }
    return render(request, 'financeiro/relatorio_whatsapp.html', stats)
```

## ðŸ’° ROI Esperado

### CobranÃ§as

- **ReduÃ§Ã£o de inadimplÃªncia:** 30-40%
- **Tempo de cobranÃ§a manual:** -80%
- **Taxa de resposta:** 60-70% (vs 20% de e-mail)

### Marketing

- **Alcance em 24h:** ~90% (vs ~20% e-mail)
- **Taxa de clique:** 25-35% (vs 2-5% e-mail)
- **ConversÃ£o em vendas:** +15-20%

### Operacional

- **Tempo economizado:** 5-10h/semana
- **SatisfaÃ§Ã£o cliente:** +40% (comunicaÃ§Ã£o proativa)

## âš ï¸ Boas PrÃ¡ticas

1. **Respeite horÃ¡rios:** NÃ£o enviar mensagens apÃ³s 20h ou antes das 8h
2. **Evite spam:** MÃ¡ximo 1 mensagem de marketing por semana por cliente
3. **OpÃ§Ã£o de sair (Opt-out):** Permitir cliente parar de receber mensagens
4. **Templates personalizados:** Use nome do cliente
5. **Rate limiting:** 1 mensagem a cada 2 segundos (evitar ban)

```python
# Implementar opt-out
class Cliente(models.Model):
    # ... campos existentes
    aceita_whatsapp = models.BooleanField(default=True)
    aceita_marketing = models.BooleanField(default=True)

def enviar_mensagem_segura(cliente, mensagem, tipo):
    if tipo == 'marketing' and not cliente.aceita_marketing:
        return False
    
    if not cliente.aceita_whatsapp:
        return False
    
    WhatsAppClient.send_message(cliente.telefone, mensagem)
    return True
```

## ðŸš€ Roadmap de ImplementaÃ§Ã£o

### Semana 1: Setup BÃ¡sico

- Escolher API (Twilio ou WWEBJS)
- Criar conta e configurar
- Testar envio de mensagem simples

### Semana 2: IntegraÃ§Ã£o Django

- Criar `whatsapp_client.py`
- Adicionar modelo `MensagemWhatsApp`
- FunÃ§Ã£o de envio com retry e logging

### Semana 3: CobranÃ§as AutomÃ¡ticas

- Implementar lembretes de pagamento
- Configurar Celery Beat
- Templates de mensagem por tipo

### Semana 4: Marketing e Extras

- Dashboard de mÃ©tricas
- Sistema de opt-out
- PromoÃ§Ãµes segmentadas

---

**Fonte:** Community  
**Risco:** MÃ©dio (se usar API nÃ£o-oficial)  
**ROI:** Muito Alto - Reduz inadimplÃªncia e aumenta engajamento


