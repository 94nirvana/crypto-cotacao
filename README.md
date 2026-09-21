# Crypto Cotação

API REST e painel web minimalista para acompanhar cotações de criptomoedas em
dólar. O serviço consulta a API pública da Binance, mantém um cache em memória
e atualiza as cotações a cada 2 segundos, ordenando os ativos pelo volume
negociado nas últimas 24 horas.

## Funcionalidades

- Consulta de preço, variação percentual e volumes de 24 horas.
- Atualização automática em segundo plano, sem exigir uma chamada à Binance a
  cada requisição do cliente.
- Fallback para consultas individuais quando a consulta agrupada à Binance
  falha.
- Painel HTML servido pela própria aplicação, com atualização automática.
- Lista fixa de ativos: `BTC`, `USDT`, `USDC`, `ETH`, `XRP`, `SOL`, `BNB`,
  `USDG`, `DOGE`, `UNI`, `TRX`, `ADA`, `XLM` e `LINK`.

## API

A aplicação inicia por padrão em `http://localhost:5000`.

### `GET /api/quotes`

Retorna todas as cotações disponíveis, em ordem decrescente de
`volume24h`:

```json
{
  "ok": true,
  "error": "",
  "timestamp": 1710000000.0,
  "quotes": [
    {
      "symbol": "BTC",
      "price": 65000.12,
      "change24h": 1.25,
      "volume24h": 12345.67,
      "quote_volume24h": 802000000.12
    }
  ]
}
```

Em caso de falha na atualização, `ok` será `false`, `error` conterá a
mensagem disponível e o campo `quotes` poderá conter o último cache válido.

### `GET /api/quotes/<symbol>`

Retorna uma cotação individual. O símbolo não diferencia maiúsculas de
minúsculas:

```bash
curl http://localhost:5000/api/quotes/btc
```

Para um ativo conhecido, a resposta tem o formato
`{"ok": true, "quote": {...}}`. Um símbolo inexistente retorna HTTP `404` com
`{"ok": false, "error": "Unknown symbol: ..."}`.

### `GET /`

Abre o painel visual de cotações. O navegador consulta `/api/quotes` a cada
2 segundos e exibe preço, variação percentual e volume de 24 horas.

## Stack

- **Python 3**
- **Flask** para a aplicação web e a API JSON
- **Requests** para as chamadas HTTP
- **Binance Spot REST API**, endpoint público
  `https://api.binance.com/api/v3/ticker/24hr`
- HTML, CSS e JavaScript embutidos no serviço; não há etapa de build frontend

## Requisitos

- Python 3.9 ou superior (o código utiliza anotações como `list[dict]`).
- Acesso à internet para consultar a Binance.

## Instalação e execução

Clone o repositório e entre na pasta do projeto:

```bash
git clone https://github.com/94nirvana/crypto-cotacao.git
cd crypto-cotacao
```

Crie e ative um ambiente virtual:

```bash
python3 -m venv venv
source venv/bin/activate
```

Instale as dependências:

```bash
python -m pip install --upgrade pip
python -m pip install Flask requests
```

Inicie o servidor:

```bash
python crypto-api/app.py
```

Acesse <http://localhost:5000> no navegador ou consulte a API com `curl`.
O processo escuta em `0.0.0.0:5000` e é iniciado sem modo debug.

## Comandos úteis

```bash
# Ativar o ambiente virtual em uma nova sessão
source venv/bin/activate

# Iniciar a aplicação
python crypto-api/app.py

# Consultar todas as cotações
curl http://localhost:5000/api/quotes

# Consultar um ativo específico
curl http://localhost:5000/api/quotes/ETH
```

## Organização

```text
.
├── crypto-api/
│   └── app.py       # Aplicação Flask, cache, integração Binance e dashboard
├── .gitignore
└── README.md
```

As dependências são instaladas diretamente no ambiente Python; o repositório
não possui arquivo de lock ou manifesto de dependências.
