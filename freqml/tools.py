import pandas as pd
import numpy as np

def CUSUM(df, threshold=0.04):
    eps = 1e-5
    diff = df["price"].diff()
    pos = diff.rolling(2).apply(lambda x: -eps if x.sum() > threshold else max(0, x.sum()), raw=True)
    neg = diff.rolling(2).apply(lambda x:  eps if x.sum() < -threshold else min(0, x.sum()), raw=True)
    idx = pos.index[pos < 0]
    neg_idx = neg.index[neg > 0]
    idx.union(neg_idx)
    return df.loc[idx, ["datetime"]].reset_index(drop=True)

def get_volatility(df, span=100, time=1):
    delta = df.index[-1] - pd.Timedelta(days=time)
    df = df[df.index.tz_localize(None) > delta.to_datetime64()]
    volatility = df["close"].ewm(span=span).std()
    return volatility