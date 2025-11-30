# Classificador - Sistema de Classificação Textual com BERT

## Visão Geral

Esse é um microsserviço de classificação textual baseado em aprendizado de máquina, projetado para identificar discurso de ódio em textos gerados por usuários. O sistema utiliza o modelo BERT pré-treinado para português (`ruanchaves/bert-base-portuguese-cased-hatebr`) em conjunto com a biblioteca Enelvo para normalização textual, garantindo processamento robusto de conteúdo em linguagem informal.

## Arquitetura

O sistema é composto por três componentes principais executados em containers Docker isolados:

### 1. Redis
Atua como broker de mensagens, gerenciando filas para comunicação assíncrona entre os serviços. Implementa três filas distintas:
- `norm_queue_in`: mensagens aguardando classificação
- `norm_queue_out`: mensagens classificadas com sucesso
- `norm_queue_errors`: mensagens que falharam no processamento

### 2. API (FastAPI)
Serviço REST que expõe endpoints para submissão e consulta de mensagens. Utiliza o padrão de processamento assíncrono, onde requisições são enfileiradas e processadas por workers dedicados.

### 3. Classificador
Worker assíncrono responsável pelo processamento batch de mensagens. Executa normalização textual via Enelvo e classificação via modelo BERT, suportando diferentes dispositivos de processamento (CPU, CUDA, MPS).

## Funcionalidades Principais

### Normalização Textual
Utiliza a biblioteca Enelvo para normalização de textos informais, corrigindo erros ortográficos comuns em redes sociais e mensagens de usuários. O normalizador é configurado via variáveis de ambiente:
- `ENELVO_FORCE_LIST`: caminho para arquivo contendo termos que devem ser forçadamente normalizados
- `ENELVO_IGNORE_LIST`: caminho para arquivo contendo termos que devem ser preservados
- `ENELVO_SANITIZE`: habilita sanitização automática de caracteres especiais (padrão: `true`)

Os arquivos de lista permitem customização do comportamento de normalização sem modificar código, sendo especialmente úteis para preservar terminologia específica do domínio ou forçar correções de termos frequentes.

### Classificação com BERT
Modelo de transformers pré-treinado que classifica textos em duas categorias:
- `0`: conteúdo não classificado como discurso de ódio
- `1`: conteúdo identificado como discurso de ódio

O modelo retorna scores de confiança para cada classificação, permitindo análise detalhada dos resultados.

### Processamento em Lote
O classificador implementa processamento batch configurável:
- `BATCH_SIZE`: número de mensagens processadas simultaneamente
- `NUM_WORKERS`: workers paralelos para processamento concorrente
- Otimização automática de throughput baseada em recursos disponíveis

## API REST

### POST `/api/enqueue`

Submete uma mensagem para classificação.

**Request Body:**
```json
{
  "msg": "Texto a ser classificado"
}
```

**Response (HTTP 202):**
```json
{
  "msg_id": "uuid-v4"
}
```

**Erros:**
- `400`: mensagem vazia ou inválida
- `500`: erro de conexão com Redis

### GET `/api/dequeue/{msg_id}`

Consulta o status de processamento de uma mensagem.

**Response (HTTP 200):**
```json
{
  "msg_id": "uuid-v4",
  "queue": "pending|completed|error"
}
```

**Status:**
- `pending`: mensagem aguardando processamento
- `completed`: classificação concluída com sucesso
- `error`: falha no processamento

**Erros:**
- `404`: mensagem não encontrada
- `500`: erro de conexão com Redis

## Estrutura de Dados

### Mensagem Enfileirada
```json
{
  "id": "uuid-v4",
  "msg": "texto original"
}
```

### Resultado de Classificação
```json
{
  "id": "uuid-v4",
  "msg": "texto original",
  "classified_at": "2025-11-29T10:30:00",
  "classification": {
    "label": "LABEL_0",
    "score": 0.9845
  },
  "status": "classified"
}
```

### Mensagem com Erro
```json
{
  "id": "uuid-v4",
  "msg": "texto original",
  "error": "descrição do erro",
  "error_type": "ValidationError|ProcessingError|UnexpectedError",
  "classified_at": "2025-11-29T10:30:00",
  "status": "error"
}
```

## Configuração

### Variáveis de Ambiente

**Redis:**
- `REDIS_HOST`: hostname do servidor Redis (padrão: `localhost`)
- `REDIS_PORT`: porta do Redis (padrão: `6379`)
- `REDIS_USER`: usuário de autenticação (padrão: `default`)
- `REDIS_PASSWORD`: senha de autenticação (opcional)

**Classificador:**
- `CLASSIFIER_DEVICE`: dispositivo de processamento (`cpu`, `cuda`, `cuda:0`, `mps`)
- `MODEL_NAME`: identificador do modelo no Hugging Face
- `NUM_WORKERS`: número de workers paralelos (padrão: `2`)
- `BATCH_SIZE`: tamanho do batch de processamento (padrão: `8`)

**Normalização Enelvo:**
- `ENELVO_IGNORE_LIST`: caminho para arquivo de termos ignorados na normalização
- `ENELVO_FORCE_LIST`: caminho para arquivo de termos forçados na normalização
- `ENELVO_SANITIZE`: habilitar sanitização de caracteres especiais (`true`/`false`)

**Logging:**
- `LOG_LEVEL`: nível de log (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`)
- `ENABLE_FILE_LOGGING`: habilitar logs em arquivo (`true`/`false`)
- `ENABLE_CONSOLE_LOGGING`: habilitar logs no console (`true`/`false`)

### Arquivo de Configuração

Crie um arquivo `.env` baseado em `.env.example`:

```bash
cp .env.example .env
```

Edite conforme necessário para seu ambiente de execução.

## Implantação com Docker

### Pré-requisitos

- Docker Engine 20.10+
- Docker Compose 2.0+
- (Opcional) NVIDIA Container Toolkit para GPU

### Inicialização Rápida

```bash
# Construir e iniciar todos os serviços
docker-compose up --build

# Executar em background
docker-compose up -d --build
```

### Escalabilidade

Execute múltiplos workers de classificação:

```bash
docker-compose up --scale classifier=3
```

### Monitoramento

Visualizar logs em tempo real:

```bash
# Todos os serviços
docker-compose logs -f

# Serviço específico
docker-compose logs -f classifier
```

### Encerramento

```bash
# Parar serviços
docker-compose down

# Remover volumes persistentes
docker-compose down -v
```

## Suporte a GPU

### NVIDIA CUDA

1. Instale o [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)

2. Descomente a seção de GPU em `docker-compose.yml`:

```yaml
classifier:
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: 1
            capabilities: [gpu]
```

3. Configure `CLASSIFIER_DEVICE=cuda` no arquivo `.env`

### Apple Silicon (MPS)

Para utilização em sistemas macOS com Apple Silicon, configure `CLASSIFIER_DEVICE=mps`. Note que o suporte MPS em containers Docker é limitado; considere execução nativa para melhor desempenho.

## Estrutura do Projeto

```
classificador/
├── app/
│   ├── __init__.py              # Inicialização do FastAPI
│   ├── processor/
│   │   ├── classifier.py        # Worker de classificação BERT
│   │   └── normaliser.py        # Normalização com Enelvo
│   ├── redis/
│   │   └── client.py            # Cliente Redis assíncrono
│   ├── routes/
│   │   └── __init__.py          # Endpoints da API
│   └── utils/
│       ├── config.py            # Configurações do sistema
│       ├── logging_config.py    # Configuração de logging
│       ├── models.py            # Modelos Pydantic
│       ├── FORCE_LIST.txt       # Lista de normalização forçada
│       └── IGNORE_LIST.txt      # Lista de termos ignorados
├── logs/                        # Diretório de logs
├── tests/                       # Testes automatizados
├── docker-compose.yml           # Orquestração de containers
├── Dockerfile.api               # Imagem do serviço API
├── Dockerfile.classifier        # Imagem do classificador
├── run.py                       # Entrypoint da API
├── run_classifier.py            # Entrypoint do classificador
├── pyproject.toml               # Dependências do projeto
└── .env.example                 # Template de configuração
```

## Tratamento de Erros

O sistema implementa tratamento robusto de erros em múltiplas camadas:

### Erros de Validação
Mensagens com formato inválido ou campos faltantes são rejeitadas e movidas para `norm_queue_errors` com `error_type: ValidationError`.

### Erros de Processamento
Falhas durante normalização ou classificação são capturadas, registradas em log e a mensagem é movida para fila de erros com `error_type: ProcessingError`.

### Erros de Infraestrutura
Problemas de conexão com Redis ou inicialização do modelo geram `error_type: UnexpectedError` e acionam mecanismos de retry.

### Graceful Shutdown
O sistema suporta encerramento gracioso, processando mensagens pendentes antes de finalizar os workers.

## Logging

O sistema implementa logging estruturado com múltiplos níveis:

### Arquivos de Log
- `classificador_YYYY-MM-DD.log`: logs rotativos diários
- Localização: `logs/` (configurável via `LOG_DIR`)

### Níveis de Log
- `DEBUG`: informações detalhadas de execução
- `INFO`: eventos normais de operação
- `WARNING`: situações anômalas não críticas
- `ERROR`: erros que não interrompem o serviço
- `CRITICAL`: falhas críticas do sistema

### Formato
```
[2025-11-29 10:30:00] [INFO] [classifier] - Completed batch of 8 messages
```

## Performance

### Otimizações Implementadas

**Processamento Assíncrono:**
- Workers não-bloqueantes para I/O com Redis
- Processamento paralelo de batches via `ProcessPoolExecutor`

**Cache de Modelos:**
- Modelos BERT carregados uma vez por worker
- Cache persistente de artefatos do Hugging Face

**Batching Inteligente:**
- Agrupamento automático de mensagens para inferência eficiente
- Timeout configurável para processar batches parciais

### Métricas Esperadas

Em configuração padrão (CPU, 2 workers, batch size 8):
- Throughput: ~50-100 mensagens/minuto
- Latência média: 5-10 segundos por mensagem
- Uso de memória: ~2GB por worker

Com GPU NVIDIA (CUDA):
- Throughput: ~200-400 mensagens/minuto
- Latência média: 1-3 segundos por mensagem
- Uso de VRAM: ~2-4GB

## Dependências

### Principais
- `fastapi`: framework web assíncrono
- `uvicorn`: servidor ASGI
- `redis`: cliente Python para Redis
- `transformers`: biblioteca Hugging Face para modelos BERT
- `torch`: backend de deep learning
- `enelvo`: normalização de textos em português

### Requisitos Completos
Consulte `pyproject.toml` para lista completa de dependências e versões.

## Desenvolvimento

### Instalação Local

```bash
# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/macOS
# ou
venv\Scripts\activate     # Windows

# Instalar dependências
pip install -e .
```

### Executar Localmente

Terminal 1 - Redis:
```bash
redis-server
```

Terminal 2 - API:
```bash
python run.py
```

Terminal 3 - Classificador:
```bash
python run_classifier.py
```

### Testes

```bash
# Enfileirar mensagem
curl -X POST "http://localhost:8000/api/enqueue" \
  -H "Content-Type: application/json" \
  -d '{"msg": "Mensagem de teste"}'

# Consultar resultado
curl "http://localhost:8000/api/dequeue/{msg_id}"
```

## Documentação Adicional

Para informações detalhadas sobre implantação e troubleshooting, consulte [DOCKER.md](DOCKER.md).

## Licença

Consulte o arquivo LICENSE para detalhes sobre licenciamento do projeto.
