
from pandas import DataFrame
from functools import reduce
from freqtrade.strategy import IStrategy, DecimalParameter, IntParameter

import talib.abstract as ta
from scipy.signal import argrelextrema
import numpy as np

class BreakoutStrategy(IStrategy):

    timeframe = "1m"
    can_short = True

    buy_atr_period = IntParameter(2, 60, default=14, space="buy")

    sell_atr_period = IntParameter(2, 60, default=14, space="sell")


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

        ilocs_max = argrelextrema(dataframe['high'].values, np.greater_equal, order=60)[0]
        dataframe.loc[
            dataframe.iloc[ilocs_max].index,
            'upper_peak'
            ] = dataframe['high']
        dataframe['upper_peak'].fillna(method='ffill', inplace=True)

        ilocs_min = argrelextrema(dataframe['low'].values, np.less_equal, order=60)[0]
        dataframe.loc[
            dataframe.iloc[ilocs_min].index,
            'lower_peak'
            ] = dataframe['low']
        dataframe['lower_peak'].fillna(method='ffill', inplace=True)

        return dataframe


    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        conditions_long = []
        conditions_short = []

        conditions_long.append(
                dataframe['close'] > dataframe['upper_peak'].shift(1)
            )

        conditions_short.append(
                dataframe['close'] < dataframe['lower_peak'].shift(1)
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
