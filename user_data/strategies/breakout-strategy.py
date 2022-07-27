
from pandas import DataFrame
from functools import reduce
from freqtrade.strategy import IStrategy, DecimalParameter, IntParameter

import talib.abstract as ta
from scipy.signal import argrelextrema
import numpy as np

class BreakoutStrategy(IStrategy):

    timeframe = "1m"
    can_short = True

    buy_peak_order = IntParameter(10, 120, default=60, space="buy")

    sell_peak_order = IntParameter(10, 120, default=60, space="sell")


    # ROI table:
    minimal_roi = {
        "0": 0.242,
        "13": 0.044,
        "51": 0.02,
        "170": 0
    }

    # Stoploss:
    stoploss = -0.271

    # Trailing stop:
    trailing_stop = True
    trailing_stop_positive = 0.01
    trailing_stop_positive_offset = 0.05
    trailing_only_offset_is_reached = False


    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        for val in self.buy_peak_order.range:
            ilocs_max = argrelextrema(dataframe['high'].values, np.greater_equal, order=val)[0]
            dataframe.loc[
                dataframe.iloc[ilocs_max].index,
                f'upper_peak_{val}'
                ] = dataframe['high']
            dataframe[f'upper_peak_{val}'].fillna(method='ffill', inplace=True)

        for val in self.sell_peak_order.range:
            ilocs_min = argrelextrema(dataframe['low'].values, np.less_equal, order=val)[0]
            dataframe.loc[
                dataframe.iloc[ilocs_min].index,
                f'lower_peak_{val}'
                ] = dataframe['low']
            dataframe[f'lower_peak_{val}'].fillna(method='ffill', inplace=True)

        return dataframe


    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        conditions_long = []
        conditions_short = []

        conditions_long.append(
                dataframe['close'] > dataframe[f'upper_peak_{self.buy_peak_order.value}'].shift(1)
            )

        conditions_short.append(
                dataframe['close'] < dataframe[f'lower_peak_{self.sell_peak_order.value}'].shift(1)
            )


        dataframe.loc[
            (
                reduce(lambda x, y: x & y, conditions_long)
            ),
            'enter_long'] = 1

        dataframe.loc[
            (
                reduce(lambda x, y: x & y, conditions_short)
            ),
            'enter_short'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        return super().populate_exit_trend(dataframe, metadata)
