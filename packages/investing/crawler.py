# import threading
import logging
import pandas as pd
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class InvestingComCrawler:
    def __init__(self):
        # Performance optimization preferences
        # Closes much of rendering
        prefs = {
            "profile.default_content_setting_values": {
                "cookies": 2,
                "images": 2,
                "javascript": 1,
                "plugins": 2,
                "popups": 2,
                "geolocation": 2,
                "notifications": 2,
                "auto_select_certificate": 2,
                "fullscreen": 2,
                "mouselock": 2,
                "mixed_script": 2,
                "media_stream": 2,
                "media_stream_mic": 2,
                "media_stream_camera": 2,
                "protocol_handlers": 2,
                "ppapi_broker": 2,
                "automatic_downloads": 2,
                "midi_sysex": 2,
                "push_messaging": 2,
                "ssl_cert_decisions": 2,
                "metro_switch_to_desktop": 2,
                "protected_media_identifier": 2,
                "app_banner": 2,
                "site_engagement": 2,
                "durable_storage": 2,
            }
        }

        opts = ChromeOptions()
        opts.add_argument("--headless")
        opts.add_experimental_option("prefs", prefs)

        svc = ChromeService()
        self.driver = webdriver.Chrome(
            options=opts,
            service=svc,
        )
        logging.info("Driver initialized")

        self.month_dict = {
            "jan": 1,
            "feb": 2,
            "mar": 3,
            "apr": 4,
            "may": 5,
            "jun": 6,
            "jul": 7,
            "aug": 8,
            "sep": 9,
            "oct": 10,
            "nov": 11,
            "dec": 12,
        }

    def crawl(self, name: str, url: str, first_only: bool = False):
        self.driver.get(url)
        logging.info("Opened the website")

        # def close_ad():
        #     current_thread = threading.current_thread()
        #     while not current_thread.stop:
        #         try:
        #             WebDriverWait(self.driver, 1).until(
        #                 EC.element_to_be_clickable(
        #                     (
        #                         By.XPATH,
        #                         '//*[@id="PromoteSignUpPopUp"]/div[2]/i',
        #                     )
        #                 )
        #             ).click()
        #         except Exception:
        #             pass

        logging.info("Expanding history")
        # Click each button to show more history
        click_cnt = 0
        while True:
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, '//*[contains(@id,"showMoreHistory")]')
                    )
                ).click()
                click_cnt += 1

            except Exception:
                break

            if first_only and click_cnt == 3:
                break
        logging.info("History expanded {} times".format(click_cnt))

        # Get predicted market data
        date_list = []
        time_list = []
        actual_list = []
        forecast_list = []
        previous_list = []

        element_xpath = self.driver.find_elements(
            By.XPATH, '//*[contains(@id,"historicEvent_")]'
        )
        for element in tqdm(element_xpath):
            td_list = element.find_elements(By.TAG_NAME, "td")
            release_date = td_list[0].text  # ex: Sep 13, 2023(Aug)
            release_time = td_list[1].text  # ex: 8:30
            actual = td_list[2].text
            forecast = td_list[3].text
            previous = td_list[4].text

            date_list.append(release_date)
            time_list.append(release_time)
            actual_list.append(actual)
            forecast_list.append(forecast)
            previous_list.append(previous)

        date_list.reverse()
        time_list.reverse()
        actual_list.reverse()
        forecast_list.reverse()
        previous_list.reverse()

        df = pd.DataFrame(
            {
                "date": date_list,
                "time": time_list,
                "actual": actual_list,
                "forecast": forecast_list,
                "previous": previous_list,
            }
        )

        return df

    def close(self):
        self.driver.close()
