
from pandas import DataFrame
from functools import reduce
from freqtrade.strategy import IStrategy
from freqtrade.exchange import timeframe_to_minutes
import freqtrade.vendor.qtpylib.indicators as qtpylib

import logging

import talib.abstract as ta

class BBBreakoutStrategy(IStrategy):

    timeframe = "3m"
    timeframe_mins = timeframe_to_minutes(timeframe)

    # ROI table:
    minimal_roi = {
        "0": 0.242,
        str(timeframe_mins * 3): 0.01,  # 2% after 3 candles
        str(timeframe_mins * 18): -0.99  # Exit after After 6 candles
    }
    # Stoploss:
    stoploss = -0.1

    # Trailing stop:
    trailing_stop = True
    trailing_stop_positive = 0.01
    trailing_stop_positive_offset = 0.05
    trailing_only_offset_is_reached = False

    count_uptrend = 0
    count_downtrend = 0

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        upperband, middleband, lowerband = ta.BBANDS(
            dataframe['close'],
            timeperiod=20
            )
        dataframe['upperband'] = upperband
        dataframe['middleband'] = middleband
        dataframe['lowerband'] = lowerband

        dataframe['begin_uptrend'] = dataframe.apply(
            lambda x: self._count_uptrend(x['close'], x['middleband'], x['upperband']), axis=1
        )

        dataframe['begin_downtrend'] = dataframe.apply(
            lambda x: self._count_uptrend(x['close'], x['middleband'], x['lowerband']), axis=1
        )

        dataframe['iii'] = self.intraday_intensity_index(dataframe)
        dataframe['iii_sum'] = dataframe['iii'].rolling(window=21).sum()
        return dataframe


    def intraday_intensity_index(self, dataframe):
        close = dataframe['close']
        high = dataframe['high']
        low = dataframe['low']
        volume = dataframe['volume']

        return ( (close * 2) - high - low ) / ( (high - low) ) * volume

    def _count_uptrend(self, close, middleband, upperband):

        if close < middleband:
            self.count_uptrend = 0

        if close > upperband:
            self.count_uptrend = self.count_uptrend + 1

        return self.count_uptrend

    def _count_downtrend(self, close, middleband, lowerband):

        if close > middleband:
            self.count_downtrend = 0

        if close < lowerband:
            self.count_downtrend = self.count_downtrend + 1

        return self.count_downtrend


    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        conditions_long = []
        conditions_short = []

        conditions_long.append(
            dataframe['close'] > dataframe['upperband']
        )
        conditions_long.append(
            (dataframe['volume'] > 0)
        )
        conditions_long.append(
            (dataframe['iii_sum'] > 0)
        )
        conditions_long.append(
            (dataframe['iii'] > 0)
        )
        conditions_long.append(
            (dataframe['begin_uptrend'] == 1)
        )

        conditions_short.append(
                dataframe['close'] < dataframe['lowerband']
            )
        conditions_short.append(
            (dataframe['iii_sum'] < 0)
        )
        conditions_short.append(
            (dataframe['volume'] > 0)
        )
        conditions_short.append(
            (dataframe['iii'] < 0)
        )
        conditions_short.append(
            (dataframe['begin_downtrend'] == 1)
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
        dataframe.loc[
            (
                (dataframe['close'] < dataframe['middleband']) &
                (dataframe['volume'] > 0)
            ),
            ['exit_long', 'exit_tag']] = (1, 'middleband_reached')

        dataframe.loc[
            (
                (dataframe['close'] > dataframe['middleband']) &
                (dataframe['volume'] > 0)
            ),
            ['exit_short', 'exit_tag']] = (1, 'middleband_reached')

        return dataframe