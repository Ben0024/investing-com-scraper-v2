import logging
import os

from packages.config.config import load_config
from packages.investing import InvestingComEngine

load_config(os.path.dirname(__file__))

if __name__ == "__main__":
    root_dir = os.path.dirname(__file__)

    custom_storage_dir = os.getenv("CUSTOM_STORAGE_DIR")
    cache_dir = os.path.join(root_dir, "cache")

    logger = logging.getLogger("main")
    logger.setLevel(logging.INFO)

    investing_com_engine = InvestingComEngine(
        custom_storage_dir=custom_storage_dir,
        logger=logger,
        cache_dir=cache_dir,
    )

    investing_com_engine.once()
