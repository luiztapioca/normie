import asyncio
import json
from concurrent.futures import ProcessPoolExecutor
from redis import RedisError
from datetime import datetime
from .normaliser import normaliser
from transformers import pipeline
from ..redis import get_async_client
from ..utils.logging_config import get_logger

logger = get_logger(__name__)


def _classify_batch_worker(batch, model_name):
    try:
        classifier = pipeline(
            "text-classification",
            model=model_name,
            device="mps",
        )
    except Exception as e:
        logger.error(f"Failed to initialize classifier pipeline: {e}")
        current_time = datetime.now().isoformat()
        return [{
            **message,
            "error": f"Model initialization failed: {str(e)}",
            "error_type": "ModelInitializationError",
            "classified_at": current_time,
            "status": "error"
        } for message in batch]
    
    results = []
    current_time = datetime.now().isoformat()
    
    for message in batch:
        try:
            if not isinstance(message, dict):
                raise ValueError(f"Invalid message format: expected dict, got {type(message).__name__}")
            
            text = message.get("msg", "")
            
            if not text or not text.strip():
                raise ValueError("Empty or missing 'msg' field in message")
            
            try:
                normalized_text = normaliser.normalise(text)
            except Exception as e:
                raise RuntimeError(f"Text normalization failed: {str(e)}")
            
            try:
                classification = classifier(normalized_text)[0]
            except Exception as e:
                raise RuntimeError(f"Classification inference failed: {str(e)}")
            
            result_message = {
                **message,
                "classification": classification,
                "classified_at": current_time,
                "status": "classified"
            }
            results.append(result_message)
            
        except ValueError as e:
            logger.warning(f"Validation error for message {message.get('id', 'unknown')}: {e}")
            error_message = {
                **message,
                "error": str(e),
                "error_type": "ValidationError",
                "classified_at": current_time,
                "status": "error"
            }
            results.append(error_message)
        except RuntimeError as e:
            logger.error(f"Processing error for message {message.get('id', 'unknown')}: {e}")
            error_message = {
                **message,
                "error": str(e),
                "error_type": "ProcessingError",
                "classified_at": current_time,
                "status": "error"
            }
            results.append(error_message)
        except Exception as e:
            logger.exception(f"Unexpected error for message {message.get('id', 'unknown')}: {e}")
            error_message = {
                **message,
                "error": f"Unexpected error: {str(e)}",
                "error_type": "UnexpectedError",
                "classified_at": current_time,
                "status": "error"
            }
            results.append(error_message)

    return results

class BERTClassifier:
    """Classification model class"""
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
        """Initialize Redis client connection
        """
        try:
            self.redis_client = await get_async_client()
        except RedisError as e:
            logger.error("error initialing redis async redis client: %s", e)
            raise

    async def start_consuming(self):
        """Consumes the queue"""
        self._running = True
        
        with ProcessPoolExecutor(max_workers=self.num_workers) as executor:
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
                            await self._process_batch(batch, executor)
                            batch = []

                    elif batch:
                        await self._process_batch(batch, executor)
                        batch = []

                except asyncio.CancelledError:
                    logger.info("Processing cancelled, shutting down gracefully")
                    break
                except RedisError as e:
                    logger.error(f"Redis connection error: {e}")
                    await asyncio.sleep(5)
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON in message: {e}")
                    await asyncio.sleep(1)
                except Exception as e:
                    logger.exception(f"Unexpected error in consumer loop: {e}")
                    await asyncio.sleep(1)

            if batch:
                await self._process_batch(batch, executor)

    async def _process_batch(self, batch, executor):
        """Processes the batch"""
        try:
            results = await asyncio.get_event_loop().run_in_executor(
                executor,
                _classify_batch_worker,
                batch,
                self.model_name
            )
            
            await self._publish_results(results)
            
            logger.info(f"Completed batch of {len(batch)} messages")
            
        except asyncio.CancelledError:
            logger.warning("Batch processing was cancelled")
            await self._handle_batch_error(batch, "Batch processing cancelled")
            raise
        except Exception as e:
            logger.exception(f"Error processing batch of {len(batch)} messages: {e}")
            await self._handle_batch_error(batch, str(e))

    async def _publish_results(self, results):
        """Publishes results to the output queue"""
        for result in results:
            message_id = result.get("id", "unknown")
            try:
                queue_name = self.output_queue if "classification" in result else self.error_queue
                
                try:
                    result_json = json.dumps(result)
                except (TypeError, ValueError) as e:
                    logger.error(f"Failed to serialize result for message {message_id}: {e}")
                    continue
                
                try:
                    await self.redis_client.lpush(queue_name, result_json)
                    await self.redis_client.hset("msg_index", message_id, queue_name)
                except RedisError as e:
                    logger.error(f"Redis error publishing result for message {message_id}: {e}")
                    raise
                
                logger.debug(f"Published result for message: {message_id}")
                
            except RedisError:
                raise
            except Exception as e:
                logger.exception(f"Unexpected error publishing result for message {message_id}: {e}")

    async def stop(self):
        """Stops the model"""
        self._running = False

        if self.redis_client:
            await self.redis_client.close()
            
        logger.info("BERT classifier stopped")
        

    async def _handle_batch_error(self, batch, error):
        """Handle errors for an entire batch by publishing to error queue

        Args:
            batch: List of messages that failed processing
            error: Error message describing the failure
        """
        for message in batch:
            message_id = message.get("id", "unknown") if isinstance(message, dict) else "unknown"
            try:
                base_message = message if isinstance(message, dict) else {"raw_message": str(message)}
                error_result = {
                    **base_message,
                    "error": error,
                    "error_type": "BatchProcessingError",
                    "classified_at": self._current_timestamp(),
                    "status": "error"
                }
                
                await self.redis_client.lpush(
                    self.error_queue,
                    json.dumps(error_result)
                )
                logger.debug(f"Published batch error for message {message_id}")
                
            except Exception as e:
                logger.error(f"Failed to publish batch error for message {message_id}: {e}")
    
    def _current_timestamp(self):
        return datetime.utcnow().isoformat()

async def test():
    try:
        bert = BERTClassifier()
    except Exception as e:
        logger.exception(f"Failed to initialize BERTClassifier: {e}")
        return
    
    await bert.initialize()
    return await bert.start_consuming()

if __name__ == '__main__':
    asyncio.run(test())
