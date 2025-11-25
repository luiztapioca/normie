from enelvo.normaliser import Normaliser
from ..utils import Config

normaliser = Normaliser(
    fc_list=Config.FORCE_LIST,
    ig_list=Config.IGNORE_LIST,
    sanitize=Config.SANITIZE
)
