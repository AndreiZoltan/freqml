import pandas as pd
import numpy as np
@pd.api.extensions.register_dataframe_accessor("bars")
class bars:
    def __init__(self, df):
       self._df = df

    @property
    def _shape(self):
        return self._df.shape

    @property
    def volume(self):
        return self._df["amount"].sum()

    @property
    def dvolume(self):
        return self._df["cost"].sum()

    @property
    def period(self):
        return self._df.loc[self._df.shape[0] - 1, "datetime"] - self._df.loc[0, "datetime"]

    #@staticmethod
    def make_bars(grouped):
        df = grouped["price"].ohlc()
        df["amount"] = grouped["amount"].sum()
        df["VWAP"] = grouped["cost"].sum() / df["amount"]
        df = df.set_index(grouped["datetime"].nth(-1))
        return df

    def plot(self, title="bars", pair="PAIR"):
        # The section of the Plotly library needed
        import plotly.graph_objects as go

        # Obtain data from the data frame
        fig = go.Figure(data=go.Candlestick(x=self._df.index,
                                     open=self._df["open"],
                                     high=self._df["high"],
                                     low=self._df["low"],
                                     close=self._df["close"]))

        # Add title and annotations
        fig.update_layout(title_text=title,
                          title={
                              'y': 0.9,
                              'x': 0.5,
                              'xanchor': 'center',
                              'yanchor': 'top'},
                          xaxis_rangeslider_visible=True, xaxis_title="Time", yaxis_title=pair)

        fig.show()


    def TIMEB(self, freq="5m"):
        grouped = self._df.groupby(pd.Grouper(key='datetime', freq=freq))
        df_TIMEB = bars.make_bars(grouped)
        return df_TIMEB


    def TB(self, m=100):
        if self._shape[0] % m != 0:
            self._df = self._df[:-(self._shape[0] % m)]
        grouped = self._df.groupby(np.floor(self._df.index / m))
        df_TB = bars.make_bars(grouped)
        return df_TB

    def VB(self, v=5000):
        self._df.loc[:, "amount_cumsum"] = self._df["amount"].cumsum()
        df_VB = self._df.loc[self._df["amount_cumsum"] <= np.floor(self.volume - (self.volume % v))]
        grouped = df_VB.groupby(np.floor(df_VB["amount_cumsum"] / v))
        del self._df["amount_cumsum"]
        df_VB = bars.make_bars(grouped)
        return df_VB

    def DB(self, d=10000):
        self._df.loc[:, "cost_cumsum"] = self._df["cost"].cumsum()
        df_DB = self._df.loc[self._df["cost_cumsum"] <= np.floor(self.dvolume - (self.dvolume % d))]
        grouped = df_DB.groupby(np.floor(df_DB["cost_cumsum"] / d))
        del self._df["cost_cumsum"]
        df_DB = bars.make_bars(grouped)
        return df_DB

    def TIB(self, theta=100):
        b_border = 0
        self._df["b"] = (self._df.loc[1:, "price"] == self._df.loc[1:, "price"].shift())
        self._df["b"] = self._df["b"].apply(lambda x: 1 if x else -1)
        self._df.loc[:, "theta"] = self._df["b"].cumsum().abs()
        self._df.loc[:, "TIB_idx"] = 0
        while self._df.loc[b_border:, "theta"].ge(theta).any():
            b_border = self._df.loc[b_border:, "theta"].eq(theta).idxmax()
            self._df.loc[b_border:, "TIB_idx"] += 1
            self._df.loc[b_border:, "theta"] -= theta
            self._df.loc[b_border:, "theta"] = self._df.loc[b_border:, "theta"].abs()
        grouped = self._df.groupby(self._df["TIB_idx"])
        self._df.drop(["TIB_idx", "b", "theta"], axis=1, inplace=True)
        df_TIB = bars.make_bars(grouped)
        return df_TIB

    def VIB(self, theta=100):
        b_border = 0
        self._df["b"] = (self._df.loc[1:, "price"] == self._df.loc[1:, "price"].shift())
        self._df.loc[:, "b"] = self._df.loc[:, "b"].apply(lambda x: 1 if x else -1)
        self._df.loc[:, "theta"] = (self._df["b"] * self._df['amount']).cumsum().abs()
        self._df.loc[:, "VIB_idx"] = 0
        while self._df.loc[b_border:, "theta"].ge(theta).any():
            b_border = self._df.loc[b_border:, "theta"].ge(theta).idxmax()
            self._df.loc[b_border:, "VIB_idx"] += 1
            self._df.loc[b_border:, "theta"] -= theta
            self._df.loc[b_border:, "theta"] = self._df.loc[b_border:, "theta"].abs()
        grouped = self._df.groupby(self._df["VIB_idx"])
        self._df.drop(["VIB_idx", "b", "theta"], axis=1, inplace=True)
        df_VIB = bars.make_bars(grouped)
        return df_VIB

    def DIB(self, theta=100):
        b_border = 0
        self._df["b"] = (self._df.loc[1:, "price"] == self._df.loc[1:, "price"].shift())
        self._df.loc[:, "b"] = self._df.loc[:, "b"].apply(lambda x: 1 if x else -1)
        self._df.loc[:, "theta"] = (self._df["b"] * self._df['cost']).cumsum().abs()
        self._df.loc[:, "DIB_idx"] = 0
        while self._df.loc[b_border:, "theta"].ge(theta).any():
            b_border = self._df.loc[b_border:, "theta"].ge(theta).idxmax()
            self._df.loc[b_border:, "DIB_idx"] += 1
            self._df.loc[b_border:, "theta"] -= theta
            self._df.loc[b_border:, "theta"] = self._df.loc[b_border:, "theta"].abs()
        grouped = self._df.groupby(self._df["DIB_idx"])
        self._df.drop(["DIB_idx", "b", "theta"], axis=1, inplace=True)
        df_DIB = bars.make_bars(grouped)
        return df_DIB

    def TRB(self):
        pass

    def VRB(self):
        pass

    def DRB(self):
        pass

