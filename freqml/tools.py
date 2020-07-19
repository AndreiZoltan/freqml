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


def volatility(df, span=100, time=1):
    delta = df.index[-1] - pd.Timedelta(days=time)
    df = df[df.index.tz_localize(None) > delta.to_datetime64()]
    df_vol = pd.DataFrame()
    df_vol["volatility"] = df["close"].ewm(span=span).std()
    return df_vol


def barriers_collisions(df, events, up=1, down=1, lapse=5):
    def collision_up(event):
        plank = df[df.index >= event[0]]
        plank = plank.loc[plank.index[0]]["close"]
        is_collision = df[df.index > event[0]].loc[:, "close"].ge(plank + up).max()
        collision_time = df[df.index > event[0]].loc[:, "close"].ge(plank + up).idxmax()
        return collision_time if is_collision else None

    def collision_down(event):
        plank = df[df.index >= event[0]]
        plank = plank.loc[plank.index[0]]["close"]
        is_collision = df[df.index > event[0]].loc[:, "close"].le(plank - down).max()
        collision_time = df[df.index > event[0]].loc[:, "close"].le(plank - down).idxmax()
        return collision_time if is_collision else None

    def collision_vert(event):
        plank = df[df.index >= event[0]]
        is_collision = plank.shape[0] > 0
        return plank.index[0] if is_collision else None

    vertical = events + pd.Timedelta(minutes=lapse)
    collisions = pd.DataFrame()
    collisions["up"] = events.apply(lambda x: collision_up(x), axis=1)
    collisions["down"] = events.apply(lambda x: collision_down(x), axis=1)
    collisions["vert"] = vertical.apply(lambda x: collision_vert(x), axis=1)
    return collisions


def labeling(df, events, up=1, down=1, lapse=5):
    def get_plank(event):
        plank = df[df.index >= event[0]]
        plank = plank.loc[plank.index[0]]["close"]
        return plank

    def axis2num(axis):
        if axis == "up":
            return 1
        elif axis == "down":
            return -1
        else:
            return 0

    df_touch = pd.DataFrame()
    collisions = barriers_collisions(df, events, up=up, down=down, lapse=lapse)
    df_touch["touch_time"] = collisions.apply(lambda x: x.min(), axis=1)
    idx = [row[0] for _, row in df_touch.iterrows()]
    df_touch["end"] = df.loc[idx, "close"].reset_index(drop=True)
    df_touch["start"] = events.apply(lambda event: get_plank(event), axis=1)
    df_touch["side"] = collisions.apply(lambda x: axis2num(x.idxmin()), axis=1)
    df_touch["size"] = np.abs(df_touch["end"] - df_touch["start"])
    df_touch["duration"] = df_touch["touch_time"] - events["datetime"]
    cols = ["start", "end", "size", "side", "duration", "touch_time"]
    return df_touch[cols]


def meta_labeling(df, events, pred_side, up=1, down=1, lapse=5):
    df_touch = labeling(df, events, up=up, down=down, lapse=lapse)
    df_touch = df_touch.rename(columns={"side": "true_side"})
    df_touch["pred_side"] = pred_side
    df_touch["take"] = df_touch["pred_side"]*df_touch["true_side"]
    df_touch.loc[df_touch["take"] < 0, "take"] = 0
    cols = ["start", "end", "size", "pred_side", "true_side", "take", "duration", "touch_time"]
    return df_touch[cols]
