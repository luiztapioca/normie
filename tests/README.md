# Testes de Carga K6 para Microsserviço de Classificação de Discurso de Ódio

Suíte de testes k6 para microsserviço de classificação de discurso de ódio em textos em português.

## Arquivos de Teste

### Suítes Implementadas

1. **smoke_test.js** - Teste de funcionalidade básica com carga mínima
   - 1 usuário virtual por 1 minuto
   - Valida operações básicas de enfileiramento/desenfileiramento
   - Verificação rápida de sanidade

2. **load_test.js** - Teste de carga padrão
   - Escalonamento de 10 a 20 usuários em 2 minutos
   - Simula carga operacional esperada
   - Utiliza todas as frases de `test_phrases.json`

3. **stress_test.js** - Teste de estresse de alta carga
   - Escala até 150 usuários concorrentes
   - Identifica limites e pontos de falha do sistema
   - Detecta gargalos de performance

4. **end_to_end_test.js** - Teste de fluxo completo
   - 5 usuários executando 30 iterações completas
   - Polling até conclusão do processamento
   - Valida ciclo completo: enfileiramento → processamento → recuperação

### Dados de Teste

- **test_phrases.json** - Dataset com 30 frases em português categorizadas:
  - `hate_speech`: Discurso de ódio explícito
  - `normal_speech`: Conteúdo neutro
  - `offensive_but_not_hate`: Linguagem ofensiva não caracterizada como ódio

## Pré-requisitos

1. Instalação do k6:
   ```bash
   # macOS
   brew install k6
   
   # Linux
   sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg \
     --keyserver hkp://keyserver.ubuntu.com:80 \
     --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
   echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" \
     | sudo tee /etc/apt/sources.list.d/k6.list
   sudo apt-get update && sudo apt-get install k6
   ```

2. Inicializar infraestrutura:
   ```bash
   docker-compose up -d
   python run_classifier.py
   ```

## Execução dos Testes

```bash
cd tests
k6 run smoke_test.js        # Smoke test
k6 run load_test.js          # Teste de carga
k6 run stress_test.js        # Teste de estresse
k6 run end_to_end_test.js    # Teste end-to-end

# URL customizada
k6 run -e BASE_URL=http://servidor:8000 load_test.js
```

## Métricas e Thresholds

### Métricas Principais

- **http_req_duration**: Latência de requisições HTTP
  - p(95): Percentil 95 do tempo de resposta
  - p(99): Percentil 99 do tempo de resposta

- **http_req_failed**: Taxa de falha de requisições

- **checks**: Taxa de validações aprovadas

- **iterations**: Iterações completas executadas

### Thresholds Definidos

| Teste | Taxa de Falha | Latência |
|-------|---------------|----------|
| Smoke | < 1% | < 200ms |
| Load | < 10% | p(95) < 500ms |
| Stress | < 30% | p(99) < 2s |
| E2E | - | > 90% checks |

### Exemplo de Output
```
     ✓ enqueue: status is 202
     ✓ dequeue: status is 200

     checks.........................: 100.00% ✓ 400  ✗ 0   
     http_req_duration..............: avg=45ms p(95)=90ms
     http_req_failed................: 0.00%   ✓ 0    ✗ 400 
     http_reqs......................: 400     20/s
```

## Troubleshooting

| Problema | Solução |
|----------|---------|
| Connection refused | Verificar API: `curl http://localhost:8000/api/enqueue` |
| Alta taxa de falha | Validar conexão Redis e recursos (CPU/memória) |
| Latência elevada | Revisar batch size do classificador e workers |

## Integração CI/CD

```bash
# Gate de smoke test
k6 run --quiet tests/smoke_test.js

# Teste de carga com exportação de resultados
k6 run --out json=results.json tests/load_test.js
```
