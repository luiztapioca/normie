import logging

# initialize -> inicialize um novo pipeline do modelo
# consumir do redis -> classificar por batches -> guardar resultados
# BERT utiliza muita CPU, portanto é CPU-bound, então pensar em uma alternativa que utilize paralelismo
# Após uma breve pesquisa, multi-processing parece ser o caminho ideal para implementar um "paralelismo"

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("BERTClassifier")


class BERTClassifier:
    def __init__(self) -> None:
        pass
