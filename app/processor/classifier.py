import logging
import asyncio
import json
from redis import RedisError
from concurrent.futures import ProcessPoolExecutor
from transformers import pipeline
from ..redis import get_client, get_async_client

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
        input_queue = "norm_queue_in",
        output_queue = "norm_queue_out",
        error_queue = "norm_queue_errors",
        model_name = "ruanchaves/bert-base-portuguese-cased-hatebr",
        num_workers = 2,
        batch_size = 8,
        poll_timeout = 1,
    ) -> None:

        self.input_queue = input_queue
        self.output_queue = output_queue
        self.error_queue = error_queue
        self.model_name = model_name
        self.num_workers = num_workers
        self.batch_size = batch_size
        self.poll_timeout = poll_timeout

        self.redis_client = None
        self._running = False

    async def initialize(self):
        """_summary_
        """
        try:
            self.redis_client = await get_async_client()
        except RedisError as e:
            logger.error("error initialing redis async redis client: %s", e)
            raise

    async def start_consuming(self):
        """Consome a fila"""
        self._running = True
        
        with ProcessPoolExecutor(max_workers=self.num_workers) as executor:
            """Fazer event loop para rodar o modelo de forma assincrona"""
            loop = asyncio.get_event_loop()
            batch = []
            
            while self._running:
                try:
                    msg_raw = await self.redis_client.brpop(
                        self.input_queue,
                        timeout=self.poll_timeout
                    )
                    
                    if msg_raw:
                        # id,msg_json = msg_raw
                        print(msg_raw)
                        
                    elif batch:
                        await self._process_batch(batch, executor, loop)
                        batch = []
                        
                except asyncio.CancelledError as e:
                    logger.info("proccess canceled: %s", e)
                    break
                except Exception as e:
                    logger.info("error in loop: %s", e)
                    await asyncio.sleep(1)

            if batch:
                await self._process_batch(batch, executor, loop)

    async def _process_batch(self, batch, executor, loop):
        """Processa o batch"""
        pass

    def _classify_batch(self):
        """Classifica o batch"""

        # usar pipeline para pegar o modelo e classificar mensagem

        pass

    async def _publish_results(self):
        """Publica os resultados na fila de output"""
        pass

    async def stop(self):
        """Para o modelo"""
        pass

# async def test():
#     try:
#         bert = BERTClassifier()
#     except Exception as e:
#         print(e)
    
#     await bert.initialize()
#     return await bert.start_consuming()

# if __name__ == '__main__':
#     asyncio.run(test())
