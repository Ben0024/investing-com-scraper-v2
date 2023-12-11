import re
import time
import datetime
import pandas as pd

from ..config.dicts import month_dict


class InvestingComPreprocessor:
    def to_numeric(self, x):
        x = str(x).strip()
        x = re.sub(r"[,()]", "", x)
        if x == "":
            return float("NaN")
        elif "%" in x:
            return float(x.strip("%"))
        elif "K" in x:
            return float(x.strip("K")) * 1000
        elif "M" in x:
            return float(x.strip("M")) * 1000000
        else:
            return float(x)

    def to_release_date(self, d, t):
        d = re.sub(r"[,()]", "", d)
        try:
            date_str = list(re.findall(r"(.*) (.\d) (\d*)", d)[0])  # Aug 21 2021
            time_struct = time.strptime(
                "{} {} {}".format(date_str[0], date_str[1], date_str[2]),
                "%b %d %Y",
            )
            date = datetime.date(
                time_struct.tm_year, time_struct.tm_mon, time_struct.tm_mday
            )

        except Exception:
            date = None

        return date

    def to_index_date(self, d, t):
        d = re.sub(r"[,()]", "", d)
        try:
            # Index date included
            date_str = list(
                re.findall(r"(.*) (.\d) (\d*) (.*)", d)[0]
            )  # Aug 21 2021 Jul

            # Check if month is in previous year
            release_month = month_dict[date_str[0].lower()]
            index_month = month_dict[date_str[3].lower()]
            year = int(date_str[2])
            if release_month < index_month:
                year -= 1

            time_struct = time.strptime(
                "{} {} {}".format(date_str[3], 1, year),
                "%b %d %Y",
            )
            date = datetime.date(time_struct.tm_year, time_struct.tm_mon, 1)

        except Exception:
            date = None

        return date

    def to_timestamp(self, date: datetime.date):
        if date is None:
            return float("NaN")
        else:
            return time.mktime(date.timetuple()) - time.timezone

    def preprocess(self, df: pd.DataFrame, name: str) -> pd.DataFrame:
        mod_df = df.copy()

        # Get Release Date if available
        mod_df["release_date"] = mod_df.apply(
            lambda x: self.to_release_date(x["date"], x["time"]), axis=1
        )

        # Get Index Date if available
        mod_df["index_date"] = mod_df.apply(
            lambda x: self.to_index_date(x["date"], x["time"]), axis=1
        )

        # Clean data
        if name == "house_start":
            # Fix release date
            index = mod_df[mod_df["date"] == "Sep 18, 2013"].index
            mod_df.loc[index, "date"] = "Aug 1, 2013"
            mod_df.loc[index, "release_date"] = datetime.date(2013, 8, 1)

        elif name == "retail_sales":
            # add back lost data
            index = mod_df[mod_df["date"] == "Feb 12, 2009"].index
            mod_df.loc[index, "date"] = "Mar 12, 2009"
            mod_df.loc[len(mod_df)] = [
                "Feb 12, 2009",
                "08:30",
                "1%",
                "-0.8%",
                "-3%",
                datetime.date(2009, 2, 12),
                datetime.date(2009, 1, 1),
            ]

            # Sort by release_date
            mod_df = mod_df.sort_values(by=["release_date"], ascending=True)
            mod_df = mod_df.reset_index(drop=True)

        elif name == "durable_mom":
            date_list = [
                "Apr 04, 2018",
                "May 03, 2018",
                "Jun 04, 2018",
                "Jul 03, 2018",
                "Sep 06, 2018",
                "Sep 05, 2019",
                "Oct 27, 2020 (Sep)",
            ]
            # drop rows with "date" in date_list
            for date in date_list:
                mod_df = mod_df[mod_df["date"] != date]

        elif name == "pending_home_sale":
            # drop all rows above Feb 01, 2008 (Jan)
            mod_df = mod_df[mod_df["release_date"] > datetime.date(2008, 2, 1)]
            mod_df = mod_df.reset_index(drop=True)

        # Get Timestamp
        mod_df["timestamp"] = mod_df.apply(
            lambda x: self.to_timestamp(x["index_date"]), axis=1
        )

        for i in range(len(mod_df) - 1, -1, -1):
            if pd.isna(mod_df["timestamp"].iloc[i]):
                # set to one month before
                dt = datetime.datetime.fromtimestamp(
                    mod_df["timestamp"].iloc[i + 1]
                ) - datetime.timedelta(days=27)
                ts = (
                    time.mktime(datetime.datetime(dt.year, dt.month, 1).timetuple())
                    - time.timezone
                )
                mod_df.loc[i, "timestamp"] = ts

        mod_df = mod_df.drop_duplicates(subset=["timestamp"], keep="last")

        return mod_df
