

Esse projeto serve o propósito de estudar a ideia de elaborar um container docker que é capaz de agir como um categorizador textual de mensagens geradas por usuário(usando a biblioteca Enelvo).

## API

A api montada no sistema é muito simples, com endpoints de `enqueue`, `result/<id>` e `status`

### `/enqueue`

Recebe a mensagem por meio do body da requisição e enfileira em uma fila Redis, retorna o ID da mensagem.

### `/result/<id>`

Retorna o resultado da categorização pelo UUID gerado pela `/enqueue`.

### `status`

Retorna um resumo geral da categorização, incluindo: mensagens categorizadas, em fila, e as que não foram possíveis de serem categorizadas.

## Classificador

O classificador é responsável por receber uma mensagem, normalizar usando o Enelvo, e retornar um resultado para uma lista no Redis; no modelo usado para esse código (ruanchaves/bert-base-portuguese-cased-hatebr) 0 ou 1, sendo 0 para mensagens que não correspondem como discurso de ódio, e 1 para mensagens que se caracterizam como discurso de ódio.

### Configuração

Configure o logging através de variáveis de ambiente no arquivo `.env`:

```env
LOG_LEVEL=INFO              # Níveis: DEBUG, INFO, WARNING, ERROR, CRITICAL
ENABLE_FILE_LOGGING=true    # Habilitar logs em arquivo
ENABLE_CONSOLE_LOGGING=true # Habilitar logs no console
```

### Arquivos de Log

Os logs são armazenados no diretório `logs/`:
