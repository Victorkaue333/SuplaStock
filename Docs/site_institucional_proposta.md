# Projeto Web: Site Institucional da SuplaStock

## VisÃ£o Geral:

O site institucional da **SuplaStock** funcionarÃ¡ como a principal vitrine digital da marca. Ele nÃ£o serÃ¡ apenas um "cartÃ£o de visitas", mas uma plataforma dinÃ¢mica, rÃ¡pida e elegante, focada em converter visitantes em clientes, transmitindo **confianÃ§a, alta performance e qualidade premium**.

Enquanto a aplicaÃ§Ã£o Django atual atua como o **sistema de gestÃ£o (ERP)** nos bastidores, o site institucional serÃ¡ a "vitrine" (Front-end) focada no pÃºblico final.

---

## ðŸŽ¨ Identidade e EstÃ©tica (Design Premium)

O site deve seguir um design moderno para gerar impacto imediato (o *"efeito WOW"*). O visual precisa alinhar a marca aos padrÃµes das grandes empresas do nicho de saÃºde e musculaÃ§Ã£o.

- **Esquema de Cores:** Modo Dark nativo (Cores profundas como preto Ã´nix, chumbo e cinza asfalto) com realces vibrantes e de alta energia (como Verde NÃ©on, Laranja ou Vermelho) para *Call to Actions* (CTAs).
- **Tipografia:** Uso de fontes sem serifa fortes, modernas e fÃ¡ceis de ler. Recomenda-se *Inter* para o corpo de texto e *Oswald* ou *Outfit* para tÃ­tulos impactantes.
- **Efeitos e AnimaÃ§Ãµes:**
  - *Glassmorphism* (efeitos de vidro translÃºcido) em cards e navbars.
  - MicrointeraÃ§Ãµes ao passar o mouse em produtos e botÃµes.
  - AnimaÃ§Ã£o de rolagem suave (scroll reveal) para apariÃ§Ã£o de elementos.
- **Fotografia:** Uso de imagens de alta resoluÃ§Ã£o com atletas, estilo de vida saudÃ¡vel e mockups de potes de suplementos de qualidade.

---

## ðŸ› ï¸ Stack TecnolÃ³gica Recomendada

Como o site institucional precisa ser extremamente veloz, bem ranqueado no Google e interativo, nÃ£o Ã© recomendado usar o motor de templates do Django padrÃ£o para ele. 

**SugestÃ£o de Stack:**

1. **Framework:** Next.js (React) ou Vite (Vanilla JS/React). *Recomendamos Next.js pela renderizaÃ§Ã£o SSR, que Ã© imbatÃ­vel para SEO.*
2. **EstilizaÃ§Ã£o:** CSS Moderno (Vanilla com VariÃ¡veis e Modular) ou Tailwind CSS (se desejado, para produtividade extrema com design atÃ´mico).
3. **ComunicaÃ§Ã£o de Dados:** Consumo de APIs (O Django atuarÃ¡ futuramente como backend para fornecer catÃ¡logo de produtos dinamicamente para o site).

---

## ðŸ—ºï¸ Mapa do Site (Estrutura de PÃ¡ginas)

O site serÃ¡ estruturado em uma Landing Page densa e pÃ¡ginas auxiliares.

### 1. Home (PÃ¡gina Principal - A Vitrine)

- **Hero Section (CabeÃ§alho):** Banner de tela cheia com vÃ­deo ou imagem de impacto, slogan da SuplaStock e um botÃ£o primÃ¡rio ("Ver Produtos" / "Comprar Agora").
- **Destaques da Marca:** SeÃ§Ã£o rÃ¡pida exibindo provas sociais ("Entrega RÃ¡pida", "Qualidade Garantida", "Atendimento via WhatsApp").
- **Carrossel de Produtos Mais Vendidos:** Display dinÃ¢mico mostrando imagem, preÃ§o e botÃ£o rÃ¡pido (esta seÃ§Ã£o consumirÃ¡ depois dados do seu Django).
- **Sobre NÃ³s:** Uma breve histÃ³ria da SuplaStock, mostrando autoridade no mercado.
- **Categorias (Whey, Creatina, PrÃ©-treino):** NavegaÃ§Ã£o visual rÃ¡pida por blocos.
- **CTA Final:** "Transforme seu treino hoje" (lead de contato).
- **Footer (RodapÃ©):** Links Ãºteis, redes sociais, polÃ­ticas de privacidade e contato.

### 2. Produtos (CatÃ¡logo)

- Grade (grid) de produtos com sistema de filtro lateral (por categoria, preÃ§o, objetivo como "Ganho de Massa" ou "Emagrecimento").
- Cards com efeito hover para ver detalhes.

### 3. Contato e LocalizaÃ§Ã£o

- FormulÃ¡rio de contato dinÃ¢mico.
- BotÃ£o/Link direto flutuante de WhatsApp (indispensÃ¡vel para o nicho).
- Mapa do Google (se houver loja fÃ­sica).

---

## ðŸš€ SEO e OtimizaÃ§Ã£o AutomÃ¡tica

O site serÃ¡ construÃ­do jÃ¡ com as melhores prÃ¡ticas de mercado:

- **Headings Corretas:** Apenas um `<h1>` por pÃ¡gina, estruturado sequencialmente.
- **Meta Tags Injetadas:** TÃ­tulos atraentes e descriÃ§Ãµes formatadas para compartilhamento em WhatsApp/Instagram (OpenGraph).
- **SemÃ¢ntica HTML5:** Uso correto de tags `<article>`, `<section>`, `<nav>`.
- **Acessibilidade:** Cores com alto contraste e links/botÃµes que informam o leitor o que fazem.

---

## User Review Required

> [!IMPORTANT]
> **DecisÃµes a tomar antes de iniciarmos o cÃ³digo:**

> 1. VocÃª concorda com a separaÃ§Ã£o onde o **Django cuida da GestÃ£o** e um **Framework Moderno Web foca na vitrine**?
> 2. Podemos seguir com um estilo visual de "Modo Dark (Escuro)" com cores fortes vibrantes para a marca?
> 3. VocÃª aprova a criaÃ§Ã£o do projeto de Front-End usando `Next.js` ou prefere algo mais simples como puro `HTML, CSS e JavaScript`?

