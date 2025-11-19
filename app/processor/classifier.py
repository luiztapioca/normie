import logging
import asyncio
import json
from concurrent.futures import ProcessPoolExecutor
from redis import RedisError
from datetime import datetime
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
            loop = asyncio.get_event_loop()
            batch = []

            while self._running:
                try:
                    msg_raw = await self.redis_client.brpop(
                        self.input_queue,
                        timeout=self.poll_timeout
                    )

                    if msg_raw:
                        _,msg_json = msg_raw
                        msg_data = json.loads(msg_json)
                        
                        batch.append(msg_data)
                        
                        if len(batch) >= self.batch_size:
                            await self._process_batch(batch, executor, loop)
                            batch = []

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
        try:
            results = await loop.run_in_executor(
                executor,
                self._classify_batch,
                batch
            )
            
            await self._publish_results(results)
            
            print(f"Completed batch of length {batch} messages")
            
        except Exception as e:
            print(f"Error processing batch: {e}")
            await self._handle_batch_error(batch, str(e))

    def _classify_batch(self, batch):
        """Classifica o batch"""

        try:
            classifier = pipeline(
                "text-classification",
                model=self.model_name,
                device="mps",
            )
            
            results = []
            for message in batch:
                try:
                    text = message["msg"]
                    classification = classifier(text)[0]
                    
                    result_message = {
                        **message,
                        "classification": classification,
                        "classified_at": self._current_timestamp(),
                        "status": "classified"
                    }
                    
                    results.append(result_message)
                    
                except Exception as e:
                    error_message = {
                        **message,
                        "error": str(e),
                        "classified_at": self._current_timestamp(),
                        "status": "error"
                    }
                    results.append(error_message)
                    
                return results
        except Exception as e:
            return[{
                **message,
                "error": f"Classification failed: {e}",
                "classified_at": self._current_timestamp(),
                "status": "error"
            } for message in batch]
            
            
    async def _publish_results(self, results):
        """Publica os resultados na fila de output"""
        for result in results:
            try:
                queue_name = self.output_queue if "classification" in result else self.error_queue
                
                await self.redis_client.lpush(
                    queue_name,
                    json.dumps(result)
                )
                
                print(f"Published result for: {result.get("id")}")
            except Exception as e:
                print(f"Error publishing result for {result.get("id"): {e}}")

    async def stop(self):
        """Para o modelo"""
        self._running = False

        if self.redis_client:
            await self.redis_client.close()
            
        print("BERT classifier stopped")
        

    async def _handle_batch_error(self, batch, error):
        """_summary_

        Args:
            batch (_type_): _description_
            error (_type_): _description_
        """
        for message in batch:
            error_result = {
                **message,
                "error": error,
                "classified_at": self._current_timestamp(),
                "status": error
            }
            
            await self.redis_client.lpush(
                self.error_queue,
                json.dumps(error_result)
            )
    
    def _current_timestamp(self):
        return datetime.utcnow().isoformat()

async def test():
    try:
        bert = BERTClassifier()
    except Exception as e:
        print(e)
    
    await bert.initialize()
    return await bert.start_consuming()

if __name__ == '__main__':
    asyncio.run(test())
