import os
import time
import logging
import multiprocessing
import pandas as pd

from ..config.sources import investing_com_sources
from .crawler import InvestingComCrawler
from .preprocessor import InvestingComPreprocessor


class InvestingComEngine:
    def __init__(
        self,
        storage_dir,
        logger: logging.Logger,
        cache_dir="cache",
    ):
        self.logger = logger
        self.storage_dir = storage_dir
        self.cache_dir = cache_dir

        self.websites = investing_com_sources
        self.crawler = InvestingComCrawler()
        self.preprocessor = InvestingComPreprocessor()

    def once(self):
        investing_com_raw_dir = os.path.join(self.cache_dir, "investing_com")
        os.makedirs(investing_com_raw_dir, exist_ok=True)

        for key, url in self.websites.items():
            # Crawling Progress
            logging.info(f"Crawling investing.com: {key}")

            raw_filepath = os.path.join(investing_com_raw_dir, f"{key}.csv")
            preprocessed_filepath = os.path.join(
                investing_com_raw_dir, f"{key}.mod.csv"
            )

            # Generate raw csv file
            if os.path.exists(raw_filepath):
                # Read raw data
                old_raw_crawled_data = pd.read_csv(raw_filepath)

                raw_crawled_data = self.crawler.crawl(
                    name=key, url=url, first_only=True
                )

                # update raw data
                raw_crawled_data = pd.concat(
                    [old_raw_crawled_data, raw_crawled_data], ignore_index=True
                )
                raw_crawled_data = raw_crawled_data.drop_duplicates(
                    subset=["date", "time"], keep="last"
                )

                # Save raw data
                raw_crawled_data.to_csv(raw_filepath, index=False)
            else:
                raw_crawled_data = self.crawler.crawl(
                    name=key, url=url, first_only=False
                )

                # Save raw data
                raw_crawled_data.to_csv(raw_filepath, index=False)

            # Generate preprocessed csv file
            raw_crawled_data = pd.read_csv(raw_filepath)

            preprocessed_crawled_data = self.preprocessor.preprocess(
                raw_crawled_data, name=key
            )

            # Save preprocessed data
            preprocessed_crawled_data.to_csv(preprocessed_filepath, index=False)

            # Generate (timestamp, val) csv file
            timestamp_df = preprocessed_crawled_data["timestamp"]

            for val_type in ["actual", "forecast", "previous"]:
                value_df = preprocessed_crawled_data[val_type].apply(
                    lambda x: self.preprocessor.to_numeric(x)
                )
                crawled_data = pd.DataFrame(
                    {"timestamp": timestamp_df, "value": value_df}
                )

                filepath = os.path.join(
                    self.storage_dir, "{}_{}".format(key, val_type), "1M.csv"
                )
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                with open(filepath, "w") as f:
                    f.write("timestamp,value\n")
                    for _, row in crawled_data.iterrows():
                        f.write("{},{}\n".format(row["timestamp"], row["value"]))

    def start(self):
        current_process = multiprocessing.current_process()

        while current_process.exitcode is None:
            try:
                self.once()
            except Exception as e:
                self.logger.error(e)
            time.sleep(60 * 60 * 24)
