import logging
import os
import time

from dotenv import load_dotenv


def load_config(root_dir: str):
    logging.basicConfig(
        level=logging.INFO, format="%(levelname)-8s %(name)-6s:  %(message)s"
    )

    MODE = os.getenv("MODE") or "dev"
    env_mode = "production" if MODE == "prod" else "development"
    env_files = [".env", f".env.{env_mode}", f".env.{env_mode}.local", ".env.local"]

    # Setup loggers
    logger = logging.getLogger("main")
    logger.setLevel(logging.INFO)

    # Create log file handler
    log_dir = os.path.join(root_dir, "logs", MODE)
    os.makedirs(log_dir, exist_ok=True)
    log_filepath = os.path.join(
        log_dir, "scraper-{}.log".format(time.strftime("%Y%m%d"))
    )
    log_file_handler = logging.FileHandler(log_filepath, encoding="utf-8")
    log_file_handler.setLevel(logging.INFO)
    log_file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(filename)s:%(lineno)d %(levelname)s %(message)s"
        )
    )
    logger.addHandler(log_file_handler)

    # Read rest of the configs
    for env_file in env_files:
        dotenv_path = os.path.join(root_dir, env_file)
        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path)
            logger.info(f"loaded {dotenv_path}")
