# Guia de Implantação Docker

## Visão Geral

Este documento descreve o processo de implantação do Classificador utilizando Docker Compose. O sistema é composto por três serviços containerizados que trabalham em conjunto para fornecer classificação textual assíncrona.

## Arquitetura de Containers

### Redis
Container baseado em `redis:7-alpine` que atua como message broker. Configurado com persistência via AOF (Append Only File) para garantir durabilidade dos dados.

**Portas expostas:** 6379

**Volumes:**
- `redis-data:/data` - persistência de dados Redis

**Health check:** ping via `redis-cli` a cada 10 segundos

### API
Container executando o serviço FastAPI responsável pelos endpoints REST. Construído a partir de `Dockerfile.api` com Python 3.12.

**Portas expostas:** 8000

**Volumes:**
- `./logs:/app/logs` - logs da aplicação
- `./app/utils/FORCE_LIST.txt:/app/app/utils/FORCE_LIST.txt` - lista de normalização forçada
- `./app/utils/IGNORE_LIST.txt:/app/app/utils/IGNORE_LIST.txt` - lista de termos ignorados

**Dependências:** aguarda Redis estar saudável antes de iniciar

### Classifier
Container executando o worker de classificação BERT. Construído a partir de `Dockerfile.classifier` com Python 3.12.

**Volumes:**
- `./logs:/app/logs` - logs da aplicação
- `model-cache:/root/.cache/huggingface` - cache de modelos do Hugging Face
- `./app/utils/FORCE_LIST.txt:/app/app/utils/FORCE_LIST.txt` - lista de normalização forçada
- `./app/utils/IGNORE_LIST.txt:/app/app/utils/IGNORE_LIST.txt` - lista de termos ignorados

**Dependências:** aguarda Redis estar saudável antes de iniciar

## Pré-requisitos

### Software Necessário
- Docker Engine 20.10 ou superior
- Docker Compose 2.0 ou superior
- Mínimo 4GB RAM disponível
- Mínimo 10GB espaço em disco (para modelos e dados)

### Configuração de GPU (Opcional)

#### NVIDIA GPU
Para utilizar GPU NVIDIA, instale o [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html):

```bash
# Ubuntu/Debian
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update
sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker
```

Verifique a instalação:
```bash
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi
```

## Configuração

### Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```bash
cp .env.example .env
```

Configure as variáveis conforme seu ambiente:

```bash
# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_USER=default
REDIS_PASSWORD=

# Classificador
CLASSIFIER_DEVICE=cpu              # cpu, cuda, cuda:0, cuda:1, mps
MODEL_NAME=ruanchaves/bert-base-portuguese-cased-hatebr
NUM_WORKERS=2
BATCH_SIZE=8

# Normalização Enelvo
ENELVO_IGNORE_LIST=/app/app/utils/IGNORE_LIST.txt
ENELVO_FORCE_LIST=/app/app/utils/FORCE_LIST.txt
ENELVO_SANITIZE=true

# Logging
LOG_LEVEL=INFO
ENABLE_FILE_LOGGING=true
ENABLE_CONSOLE_LOGGING=true
```

### Configuração de GPU

Para habilitar suporte a GPU NVIDIA, edite `docker-compose.yml` e descomente a seção:

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

Então configure `CLASSIFIER_DEVICE=cuda` no arquivo `.env`.

### Listas de Normalização Personalizadas

Para utilizar listas customizadas de normalização:

1. Edite os arquivos `app/utils/FORCE_LIST.txt` e `app/utils/IGNORE_LIST.txt`
2. Ou configure caminhos customizados via `ENELVO_FORCE_LIST` e `ENELVO_IGNORE_LIST`

## Operações

### Construção e Inicialização

Construir imagens e iniciar todos os serviços:

```bash
docker-compose up --build
```

Executar em modo detached (background):

```bash
docker-compose up -d --build
```

Reconstruir apenas um serviço específico:

```bash
docker-compose build api
docker-compose build classifier
```

### Verificação de Status

Listar containers em execução:

```bash
docker-compose ps
```

Verificar saúde dos serviços:

```bash
docker-compose ps
# Status deve mostrar "healthy" para redis
```

### Visualização de Logs

Todos os serviços:

```bash
docker-compose logs -f
```

Serviço específico:

```bash
docker-compose logs -f api
docker-compose logs -f classifier
docker-compose logs -f redis
```

Últimas N linhas:

```bash
docker-compose logs --tail=100 classifier
```

### Escalabilidade

Executar múltiplas instâncias do classificador:

```bash
docker-compose up --scale classifier=3
```

**Atenção:** Ao escalar, considere:
- Recursos de CPU/GPU disponíveis
- Memória RAM necessária (~2GB por worker)
- VRAM da GPU (se aplicável, ~2-4GB por worker)

### Parada e Remoção

Parar serviços mantendo volumes:

```bash
docker-compose down
```

Parar e remover volumes (dados serão perdidos):

```bash
docker-compose down -v
```

Parar apenas um serviço:

```bash
docker-compose stop classifier
```

Reiniciar serviço:

```bash
docker-compose restart api
```

## Acesso aos Serviços

### API REST

URL base: `http://localhost:8000`

Documentação interativa (Swagger): `http://localhost:8000/docs`

Exemplo de uso:

```bash
# Enfileirar mensagem
curl -X POST "http://localhost:8000/api/enqueue" \
  -H "Content-Type: application/json" \
  -d '{"msg": "Texto para classificar"}'

# Resposta: {"msg_id": "uuid-aqui"}

# Consultar status
curl "http://localhost:8000/api/dequeue/{msg_id}"
```

### Redis

Acesso direto ao Redis (para debug):

```bash
docker-compose exec redis redis-cli

# Comandos úteis:
> LLEN norm_queue_in      # Tamanho da fila de entrada
> LLEN norm_queue_out     # Tamanho da fila de saída
> LLEN norm_queue_errors  # Tamanho da fila de erros
> HLEN msg_index          # Total de mensagens indexadas
> KEYS *                  # Listar todas as chaves
```

## Troubleshooting

### Container não inicia

**Sintoma:** Container reinicia continuamente

**Diagnóstico:**
```bash
docker-compose logs classifier
docker-compose ps
```

**Possíveis causas:**
- Redis não disponível: aguarde health check do Redis
- Modelo não carregado: verifique espaço em disco e conectividade
- Configuração inválida: valide variáveis de ambiente

### Erro de conexão com Redis

**Sintoma:** `ConnectionError: Error connecting to Redis`

**Solução:**
1. Verifique se Redis está rodando: `docker-compose ps redis`
2. Confirme `REDIS_HOST=redis` no `.env`
3. Reinicie os serviços: `docker-compose restart`

### GPU não detectada

**Sintoma:** `RuntimeError: CUDA not available`

**Solução:**
1. Verifique drivers NVIDIA: `nvidia-smi`
2. Confirme instalação do toolkit: `docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi`
3. Verifique configuração no `docker-compose.yml`
4. Confirme `CLASSIFIER_DEVICE=cuda` no `.env`

### Erro de memória (OOM)

**Sintoma:** `RuntimeError: CUDA out of memory` ou container killed

**Solução:**
- Reduza `BATCH_SIZE` no `.env` (tente 4 ou 2)
- Reduza `NUM_WORKERS` no `.env`
- Use modelo menor ou CPU
- Aumente memória alocada ao Docker

### Download lento do modelo

**Sintoma:** Primeiro start muito demorado

**Explicação:** Normal na primeira execução. O modelo BERT (~500MB) é baixado do Hugging Face.

**Solução:**
- Aguarde a conclusão do download
- Modelo é cacheado no volume `model-cache`
- Próximas inicializações serão rápidas

### Fila crescendo indefinidamente

**Sintoma:** `norm_queue_in` aumenta constantemente

**Diagnóstico:**
```bash
docker-compose exec redis redis-cli LLEN norm_queue_in
```

**Solução:**
- Escale classificadores: `docker-compose up --scale classifier=3`
- Aumente `BATCH_SIZE` no `.env`
- Aumente `NUM_WORKERS` no `.env`
- Considere usar GPU

### Logs não aparecem

**Sintoma:** Comando `docker-compose logs` não mostra saída

**Solução:**
1. Verifique `ENABLE_CONSOLE_LOGGING=true` no `.env`
2. Verifique `LOG_LEVEL` (use `DEBUG` para mais detalhes)
3. Reinicie serviços após alterar `.env`

## Monitoramento

### Métricas Redis

Obter estatísticas Redis:

```bash
docker-compose exec redis redis-cli INFO stats
docker-compose exec redis redis-cli INFO memory
```

### Uso de Recursos

Monitorar recursos dos containers:

```bash
docker stats
```

### Logs Persistentes

Logs são salvos em `./logs/`:
- Rotação diária automática
- Formato: `normie_YYYY-MM-DD.log`

## Manutenção

### Limpeza de Dados

Remover mensagens antigas do Redis:

```bash
docker-compose exec redis redis-cli FLUSHALL
```

**Atenção:** Isso remove TODOS os dados do Redis.

### Atualização de Modelos

Para forçar re-download do modelo:

```bash
docker-compose down
docker volume rm classificador_model-cache
docker-compose up --build
```

### Backup

Backup dos dados Redis:

```bash
docker-compose exec redis redis-cli SAVE
docker cp $(docker-compose ps -q redis):/data/dump.rdb ./backup/
```

Restaurar backup:

```bash
docker-compose down
docker cp ./backup/dump.rdb $(docker-compose ps -q redis):/data/
docker-compose up
```

## Segurança

### Recomendações para Produção

1. **Redis com Senha:**
   ```bash
   REDIS_PASSWORD=senha-forte-aqui
   ```

2. **Rede Isolada:**
   - Não exponha porta Redis (6379) publicamente
   - Use reverse proxy (nginx) na frente da API

3. **Limite de Recursos:**
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '2.0'
         memory: 4G
   ```

4. **Volumes com Permissões:**
   ```bash
   chmod 750 logs/
   ```

5. **Health Checks:**
   - Configure health checks customizados para API e Classifier
   - Implemente monitoramento externo

6. **Logs Sensíveis:**
   - Evite logar conteúdo de mensagens em produção
   - Use `LOG_LEVEL=WARNING` ou `ERROR`

## Performance

### Tunning de Configuração

Para máximo throughput:

```bash
# CPU (múltiplos cores)
NUM_WORKERS=4
BATCH_SIZE=16

# GPU única
NUM_WORKERS=2
BATCH_SIZE=32
CLASSIFIER_DEVICE=cuda

# Múltiplas GPUs
# Escale containers e atribua dispositivos específicos
docker-compose up --scale classifier=2
# Configure cada instância com cuda:0, cuda:1, etc.
```

### Benchmarking

Teste de carga básico:

```bash
# Enfileirar múltiplas mensagens
for i in {1..100}; do
  curl -X POST "http://localhost:8000/api/enqueue" \
    -H "Content-Type: application/json" \
    -d "{\"msg\": \"Mensagem de teste $i\"}" &
done
wait

# Monitorar processamento
watch -n 1 'docker-compose exec redis redis-cli LLEN norm_queue_in'
```

## Integração Contínua

### Build Automatizado

Exemplo de pipeline CI/CD:

```yaml
# .github/workflows/docker.yml
name: Docker Build

on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build images
        run: |
          docker-compose build
      - name: Run tests
        run: |
          docker-compose up -d
          # Adicionar testes aqui
          docker-compose down
```

## Suporte

Para problemas não cobertos neste guia:

1. Verifique logs detalhados: `docker-compose logs --tail=500`
2. Consulte documentação do projeto no README.md
3. Reporte issues no repositório GitHub

## Referências

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/)
- [Redis Docker Official Image](https://hub.docker.com/_/redis)
- [Hugging Face Transformers](https://huggingface.co/docs/transformers/)
