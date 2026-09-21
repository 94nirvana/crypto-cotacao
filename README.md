# 🪙 Crypto Cotação API & Dashboard

Uma aplicação moderna para **consulta, monitoramento e rastreamento de cotações de criptomoedas em tempo real**, desenvolvida com foco em alta performance, resiliência na integração com APIs de terceiros, **Clean Architecture** e princípios de **Security by Design**.

---

## 📌 Índice

- [Visão Geral](#-visão-geral)
- [Arquitetura e Tecnologias](#-arquitetura-e-tecnologias)
- [Funcionalidades Principais](#-funcionalidades-principais)
- [Práticas de Segurança (AppSec) e Resiliência](#-práticas-de-segurança-appsec-e-resiliência)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Pré-requisitos](#-pré-requisitos)
- [Instalação e Execução](#-instalação-e-execução)
- [Variáveis de Ambiente](#-variáveis-de-ambiente)
- [Endpoints da API](#-endpoints-da-api)
- [Licença](#-licença)

---

## 📑 Visão Geral

O **Crypto Cotação** é um sistema projetado para consumir, agregar e disponibilizar dados atualizados do mercado de criptoativos (ex: Bitcoin, Ethereum, Solana, Stablecoins). O projeto provê dados precisos sobre preços, variações percentuais em tempo real, volumes de negociação e histórico de cotações para conversão com moedas fiduciárias (USD, BRL, EUR).

---

## 🛠 Arquitetura e Tecnologias

### **Back-End / API**
- **Node.js** com **TypeScript** / **JavaScript (ES6+)**
- **Framework Web:** Express.js (Arquitetura RESTful)
- **Integração Externa:** Axios / Fetch API com políticas de retry e timeout curto
- **Cache & Armazenamento:** Redis (para caching de alto desempenho e mitigação de rate limit de APIs terceiras) / PostgreSQL ou MongoDB
- **Validação de Dados:** Zod / Joi para validação e sanitização estrita de payloads de entrada e saída
- **Gerenciamento de Taxas:** Rate Limit por IP/Client ID

### **Front-End (se aplicável)**
- **React.js** / **Next.js** / HTML5 & CSS3
- **Gráficos & Visualização:** Chart.js / Recharts (para renderização de gráficos financeiros de cotação)
- **Comunicação em Tempo Real:** WebSockets / SSE (Server-Sent Events) para atualizações sem polling desnecessário

---

## ⚡ Funcionalidades Principais

- 📈 **Cotações em Tempo Real:** Consulta atualizada de preços das principais criptomoedas do mercado.
- 💱 **Conversor de Moedas:** Conversão dinâmica entre criptoativos e moedas fiduciárias (BRL, USD, EUR).
- 📊 **Histórico e Tendências:** Gráficos interativos com histórico de preços e variação percentual (24h, 7d, 30d).
- ⚡ **Cache Inteligente:** Armazenamento em memória (Redis) para evitar *rate-limit* nas APIs financeiras externas e reduzir latência de resposta.
- 🔔 **Alertas de Preço (Opcional):** Notificação quando um criptoativo atinge determinado patamar de preço.

---

## 🛡️ Práticas de Segurança (AppSec) e Resiliência

Para lidar com dados financeiros e consumo de APIs externas com estabilidade, foram aplicadas as seguintes regras de segurança e engenharia:

1. **Proteção contra Over-fetching e Rate Limit Externo:** Implementação de camada de cache inteligente (Redis) que reduz requisições redundantes a provedores externos de cotação (ex: CoinGecko, Binance API).
2. **Sanitização e Validação Estrita (Fail Fast):** Toda entrada do usuário (símbolos de cripto, moedas alvo, intervalos de datas) é estritamente validada usando Zod/Joi para prevenir ataques como Injection e SSRF (Server-Side Request Forgery).
3. **Cabeçalhos HTTP Seguros:** Utilização de `helmet` para configurar diretivas seguras de CSP, HSTS e prevenção de sniffing de MIME type.
4. **Resiliência & Circuit Breaker:** Tratamento de falhas em APIs de cotação de terceiros com suporte a fallback de dados em cache e respostas graciosas em caso de instabilidade externa.
5. **Gerenciamento de API Keys:** Nenhuma chave de API ou segredo é versionada no repositório; todas são injetadas exclusivamente via `.env`.

---

## 📂 Estrutura do Projeto

```text
crypto-cotacao/
├── src/
│   ├── config/          # Configurações de API, Redis, CORS e parâmetros globais
│   ├── controllers/     # Handlers das rotas de cotação e conversão
│   ├── middlewares/     # Middlewares de validação, cache, rate limit e erro
│   ├── services/        # Lógica de integração com APIs de cripto e cálculo financeiro
│   ├── routes/          # Definição dos endpoints REST
│   ├── utils/           # Helper para formatação de moedas e tratamento de exceções
│   └── app.js / server.js # Ponto de partida do servidor
├── .env.example         # Template de variáveis de ambiente
├── package.json         # Scripts e dependências do projeto
└── README.md            # Documentação do repositório
