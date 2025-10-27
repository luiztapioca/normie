import logging
from ..redis import get_client

# initialize -> inicialize um novo pipeline do modelo
# consumir do redis -> classificar por batches -> guardar resultados
# BERT utiliza muita CPU, portanto é CPU-bound, então pensar em uma alternativa que utilize paralelismo
# Após uma breve pesquisa, multi-processing parece ser o caminho ideal para implementar um "paralelismo"

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("BERTClassifier")


class BERTClassifier:
    """Classe do modelo de classificacao"""
    def __init__(
        self,
        redis = get_client,
        input_queue = "norm_queue_in",
        output_queue = "norm_queue_out",
        error_queue = "norm_queue_errors",
        model_name = "ruanchaves/bert-base-portuguese-cased-hatebr",
        num_workers = 2,
        batch_size = 8,
        poll_timeout = 1
    ) -> None:

        self.redis = redis
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.error_queue = error_queue
        self.model_name = model_name
        self.num_workers = num_workers
        self.batch_size = batch_size
        self.poll_timeout = poll_timeout


    async def initialize(self):
        """Inicializa o modelo"""
        pass

    async def start_consuming(self):
        """Consome a fila"""
        pass

    async def _process_batch(self):
        """Processa o batch"""
        pass

    def _classify_batch(self):
        """Classifica o batch"""
        pass

    async def _publish_results(self):
        """Publica os resultados na fila de output"""
        pass

    async def stop(self):
        """Para o modelo"""
        pass
