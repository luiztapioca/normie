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
        pass

    async def initialize(self):
        pass

    async def start_consuming(self):
        pass

    async def _process_batch(self):
        pass

    def _classify_batch(self):
        pass

    async def _publish_results(self):
        pass

    async def stop(self):
        pass
