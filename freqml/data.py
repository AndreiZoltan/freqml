from datetime import datetime
import pandas as pd
import shutil
import os


class Side:
    def __init__(self, current_side):
        self.current_side = current_side

    def side(self, x):
        if x[1] < x[0]:
            self.current_side = -1
            return -1
        elif x[1] > x[0]:
            self.current_side = 1
            return 1
        else:
            return self.current_side


def process_dataset(df):
    df = df.rename(columns={"a": "id",
                            "p": "price",
                            "q": "amount",
                            "T": "timestamp"})
    s = Side(0)
    df["price"] = pd.to_numeric(df["price"])
    df["amount"] = pd.to_numeric(df["amount"])
    df["side"] = df["price"].rolling(2).apply(lambda x: s.side(x), raw=True)
    df["cost"] = df["price"] * df["amount"]
    del df["f"]
    del df["l"]
    del df["m"]
    del df["M"]
    return df.reset_index(drop=True)


def gather_dataset(path):
    files = os.listdir(path)
    files = sorted(files)
    files = [str(path + '/' + f ) for f in files]
    df = pd.concat((pd.read_csv(f, index_col=0) for f in files), ignore_index=True)
    df = df.dropna()
    return df


def load_dataset(client,
                 pair='ETHUSDT',
                 days=1,
                 path='/home/zoltan/github/freqml/data/',
                 override=False):
    new_folder = path + '/' + pair + '_' + str(days)
    path_dir = "/".join(new_folder.split('/')[:-1])
    name_csv = new_folder.split('/')[-1]
    filename = path_dir + '/' + name_csv + '.csv'
    if os.path.exists(filename) and override is False:
        dtypes = {'id': 'int',
                  'price': 'float',
                  'amount': 'float',
                  'timestamp': 'long',
                  'side': 'float',
                  'cost': 'float'}
        df = pd.read_csv(filename,
                         index_col=0,
                         dtype=dtypes)
        return df
    if os.path.exists(new_folder):
        shutil.rmtree(new_folder)
    os.mkdir(new_folder)
    end = int(datetime.now().timestamp()*1000)
    start = int(end - days*24*60*60*1000)
    step = int(60*60*1000)
    while True:
        trades = client.get_aggregate_trades(symbol=pair,
                                             startTime=start,
                                             endTime=start + step)
        df = pd.DataFrame(trades)
        df.to_csv(new_folder + '/' + str(start) + '.csv')
        if start + step >= end:
            step = end - start
            start += step
            if step <= 0:
                break
        else:
            start += step
    df = gather_dataset(new_folder)
    df = process_dataset(df)
    df.to_csv(filename)
    shutil.rmtree(new_folder)
    return df
