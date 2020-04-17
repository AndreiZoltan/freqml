import os
import pandas as pd
from freqml.json2csv import json2csv

abs_path = os.path.abspath(__file__)
freqml_path = "/".join(abs_path.split("/")[:-2])
freqtr_user_path = freqml_path + "/freqtrade/user_data/data/"


def get_filepath(curr1, curr2="USDT", days="1", exchange="binance"):
    path = freqtr_user_path + exchange + "/"
    file = curr1 + "_" + curr2 + "-trades--" + days + "d" + ".csv"
    return path + file


def clear(df):
    del df['takerOrMaker']
    del df['fee']
    del df['info']
    del df['symbol']
    #del df['timestamp']
    del df['type']
    del df['order']
    df["id"] = df["id"] - df["id"].min()
    df['datetime'] = pd.to_datetime(df["datetime"])


def load(curr1, curr2="USDT", exchange="binance", days="1"):
    filepath = get_filepath(curr1, curr2, days, exchange)
    if os.path.isfile(filepath) == True:
        os.remove(filepath)
    command =   "cd " + freqml_path + "/freqtrade &&"\
              + "freqtrade download-data"\
              + " --exchange " + exchange \
              + " --pairs " + curr1 + "/" + curr2 \
              + " --datadir user_data/data/" + exchange \
              + " --days " + str(days) \
              + " -v --erase --dl-trades"
    os.system(command)
    os.system("gunzip " + filepath.split("--")[0] + ".json.gz")
    json2csv(filepath.split("--")[0] + ".json",
             filepath)
    os.system("cd " + freqtr_user_path + exchange + "/ &&" \
              + "rm " + "*.json")


def read(curr1, curr2="USDT", exchange="binance", days="1", override=False):
    filepath = get_filepath(curr1=curr1, curr2=curr2, days=days, exchange=exchange)
    if os.path.isfile(filepath) == False or override == True:
        load(curr1, curr2, exchange, days)
    df = pd.read_csv(filepath)
    clear(df)
    return df


def big_read(curr1, curr2="USDT", exchange="binance", days="1", override=False):
    filepath = get_filepath(curr1=curr1, curr2=curr2, days=days, exchange=exchange)
    if os.path.isfile(filepath) == False or override == True:
        load(curr1, curr2, exchange, days)
    df_parted = pd.read_csv(filepath, chunksize=1000000)
    return df_parted


def read2(curr11, curr21, curr12="USDT", curr22="USDT", exchange="binance", days="1", override=False):
    filepath1 = get_filepath(curr1=curr11, curr2=curr12, days=days, exchange=exchange)
    filepath2 = get_filepath(curr1=curr21, curr2=curr22, days=days, exchange=exchange)
    if os.path.isfile(filepath1) == False or override == True:
        load(curr11, curr12, exchange, days)
    if os.path.isfile(filepath2) == False or override == True:
        load(curr21, curr22, exchange, days)
    df1 = pd.read_csv(filepath1)
    df2 = pd.read_csv(filepath2)
    clear(df1)
    clear(df2)
    start = max(pd.to_datetime(df1["datetime"][0]), pd.to_datetime(df2["datetime"][0]))
    end = min(pd.to_datetime(df1["datetime"].iloc[-1]), pd.to_datetime(df2["datetime"].iloc[-1]))
    df1 = df1[df1["datetime"] >= start]
    df2 = df2[df2["datetime"] >= start]
    df1 = df1[df1["datetime"] <= end]
    df2 = df2[df2["datetime"] <= end]
    return df1, df2