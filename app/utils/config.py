from typing import final
import os


@final
class Config:
    BASEDIR = os.path.dirname(os.path.abspath(__file__))

    IGNORE_LIST: str = os.path.join(BASEDIR, "IGNORE_LIST.txt")
    FORCE_LIST: str = os.path.join(BASEDIR, "FORCE_LIST.txt")
