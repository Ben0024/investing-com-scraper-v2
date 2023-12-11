import os
import logging
from multiprocessing import Process
from packages.config.config import load_config
from packages.investing import InvestingComEngine

load_config(os.path.dirname(__file__))

if __name__ == "__main__":
    # basic dir
    root_dir = os.path.dirname(__file__)
    investing_storage_dir = os.getenv("INVESTING_STORAGE_DIR")
    cache_dir = os.path.join(root_dir, "cache")

    # Setup loggers
    logger = logging.getLogger("main")
    logger.setLevel(logging.INFO)
    if investing_storage_dir is None or root_dir is None:
        logger.error("INVESTING_STORAGE_DIR or root_dir is not set")
        exit(1)

    # Run forever
    processes: list[Process] = []
    investing_com_engine = InvestingComEngine(
        storage_dir=investing_storage_dir,
        logger=logger,
        cache_dir=cache_dir,
    )
    processes.append(Process(target=investing_com_engine.start))

    for p in processes:
        p.daemon = True
        p.start()

    while True:
        cmd = input()
        if cmd.lower() in ["q", "quit", "exit"]:
            for p in processes:
                p.terminate()
            break
