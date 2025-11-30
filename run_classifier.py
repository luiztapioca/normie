"""Classifier worker startup script"""
import asyncio
import os
from app.processor.classifier import BERTClassifier
from app.utils.logging_config import setup_logging, get_logger

logger = get_logger(__name__)


async def main():
    """Main entry point for classifier worker"""
    
    # Setup logging
    setup_logging(
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        log_dir="/app/logs",
        enable_file_logging=os.getenv("ENABLE_FILE_LOGGING", "true").lower() == "true",
        enable_console_logging=True
    )
    
    # Get configuration from environment variables
    device = os.getenv("CLASSIFIER_DEVICE", "cpu")
    model_name = os.getenv(
        "MODEL_NAME", 
        "ruanchaves/bert-base-portuguese-cased-hatebr"
    )
    num_workers = int(os.getenv("NUM_WORKERS", "2"))
    batch_size = int(os.getenv("BATCH_SIZE", "8"))
    
    logger.info("Starting BERT Classifier worker")
    logger.info(f"Device: {device}")
    logger.info(f"Model: {model_name}")
    logger.info(f"Workers: {num_workers}")
    logger.info(f"Batch size: {batch_size}")
    
    classifier = BERTClassifier(
        device=device,
        model_name=model_name,
        num_workers=num_workers,
        batch_size=batch_size
    )
    
    try:
        await classifier.initialize()
        logger.info("Classifier initialized successfully")
        await classifier.start_consuming()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    except Exception as e:
        logger.exception(f"Error running classifier: {e}")
        raise
    finally:
        await classifier.stop()
        logger.info("Classifier stopped")


if __name__ == "__main__":
    asyncio.run(main())
