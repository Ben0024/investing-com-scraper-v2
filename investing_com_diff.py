import os

import pandas as pd


def check_versions():
    cache_dir = os.path.join(os.path.dirname(__file__), "cache")

    raw_dir = os.path.join(cache_dir, "investing_com.0906.raw")
    latest_dir = os.path.join(cache_dir, "investing_com")

    for filename in os.listdir(raw_dir):
        if not filename.endswith(".csv"):
            continue

        raw_filepath = os.path.join(raw_dir, filename)
        raw_df = pd.read_csv(raw_filepath)

        latest_filepath = os.path.join(latest_dir, filename)
        if not os.path.exists(latest_filepath):
            continue
        latest_df = pd.read_csv(latest_filepath)

        # print date in raw not in latest
        diff_list = []
        for date in raw_df["date"].unique():
            if date not in latest_df["date"].unique():
                diff_list.append(date)

        if diff_list:
            print(filename, raw_filepath, latest_filepath)
            print(raw_df[raw_df["date"].isin(diff_list)])
            print()

        diff_list = []
        for date in latest_df["date"].unique():
            if date not in raw_df["date"].unique():
                diff_list.append(date)

        if diff_list:
            print(filename, latest_filepath, raw_filepath)
            print(latest_df[latest_df["date"].isin(diff_list)])
            print()


def check_preprocess():
    cache_dir = os.path.join(os.path.dirname(__file__), "cache")
    raw_dir = os.path.join(cache_dir, "investing_com")

    for filename in os.listdir(raw_dir):
        if not filename.endswith(".csv") or filename.endswith(".mod.csv"):
            continue

        raw_filepath = os.path.join(raw_dir, filename)
        mod_filepath = os.path.join(raw_dir, filename.replace(".csv", ".mod.csv"))

        raw_df = pd.read_csv(raw_filepath)
        mod_df = pd.read_csv(mod_filepath)

        diff_list = []
        for date in raw_df["date"].unique():
            if date not in mod_df["date"].unique():
                diff_list.append(date)

        if diff_list:
            print(filename, raw_filepath, mod_filepath)
            print(raw_df[raw_df["date"].isin(diff_list)])
            print()

        diff_list = []
        for date in mod_df["date"].unique():
            if date not in raw_df["date"].unique():
                diff_list.append(date)

        if diff_list:
            print(filename, mod_filepath, raw_filepath)
            print(mod_df[mod_df["date"].isin(diff_list)])
            print()


if __name__ == "__main__":
    check_versions()
    check_preprocess()
