# Normie

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

## Logging

O sistema possui um sistema de logging centralizado e configurável:

### Configuração

Configure o logging através de variáveis de ambiente no arquivo `.env`:

```env
LOG_LEVEL=INFO              # Níveis: DEBUG, INFO, WARNING, ERROR, CRITICAL
ENABLE_FILE_LOGGING=true    # Habilitar logs em arquivo
ENABLE_CONSOLE_LOGGING=true # Habilitar logs no console
```

### Arquivos de Log

Os logs são armazenados no diretório `logs/`:

- **app.log** - Log geral da aplicação (rotação automática a cada 10MB)
- **error.log** - Apenas erros (ERROR e CRITICAL)

### Uso no Código

```python
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

logger.debug("Mensagem de debug")
logger.info("Informação geral")
logger.warning("Aviso")
logger.error("Erro")
logger.exception("Erro com stack trace")
```


[TODO]:

- [ ] imagem docker do serviço

- [ x ] filas usando redis

- [ ] implementar categorização via BERTimbau

- [ ] fazer middleware para tratamento de erros
