
from pandas import DataFrame
from functools import reduce
from freqtrade.strategy import IStrategy, IntParameter

import talib.abstract as ta

class BollingerBandStrategy(IStrategy):

    timeframe = "3m"

    # ROI table:
    minimal_roi = {
        "0": 0.242,
        "13": 0.044,
        "51": 0.02,
        "170": 0
    }

    # Stoploss:
    stoploss = -0.1

    # Trailing stop:
    trailing_stop = True
    trailing_stop_positive = 0.01
    trailing_stop_positive_offset = 0.05
    trailing_only_offset_is_reached = False

    bars_delay_long = 0
    bars_delay_short = 0

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        upperband, middleband, lowerband = ta.BBANDS(dataframe)
        dataframe['upperband'] = upperband
        dataframe['middleband'] = middleband
        dataframe['lowerband'] = lowerband

        return dataframe


    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        conditions_long = []
        conditions_short = []

        conditions_long.append(
                dataframe['close'] > dataframe['upperband']
            )



        conditions_short.append(
                dataframe['close'] < dataframe['lowerband']
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
