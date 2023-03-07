
from pandas import DataFrame
from functools import reduce
from freqtrade.strategy import IStrategy
from freqtrade.exchange import timeframe_to_minutes


import talib.abstract as ta

class BollingerBandStrategy(IStrategy):

    timeframe = "3m"
    timeframe_mins = timeframe_to_minutes(timeframe)

    # ROI table:
    minimal_roi = {
        "0": 0.242,
        str(timeframe_mins * 3): 0.01,  # 2% after 3 candles
        str(timeframe_mins * 6): 0.00  # 1% After 6 candles
    }
    # Stoploss:
    stoploss = -0.1

    # Trailing stop:
    trailing_stop = True
    trailing_stop_positive = 0.01
    trailing_stop_positive_offset = 0.05
    trailing_only_offset_is_reached = False


    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        upperband, middleband, lowerband = ta.BBANDS(
            dataframe['close'],
            timeperiod=20
            )
        dataframe['upperband'] = upperband
        dataframe['middleband'] = middleband
        dataframe['lowerband'] = lowerband

        dataframe['iii'] = self.intraday_intensity_index(dataframe)

        return dataframe


    def intraday_intensity_index(self, dataframe):
        close = dataframe['close']
        high = dataframe['high']
        low = dataframe['low']
        volume = dataframe['volume']

        return ( (close * 2) - high - low ) / ( (high - low) * volume )

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        conditions_long = []
        conditions_short = []

        conditions_long.append(
            dataframe['close'] < dataframe['lowerband']
        )
        conditions_long.append(
            (dataframe['volume'] > 0)
        )

        conditions_short.append(
                dataframe['close'] > dataframe['upperband']
            )
        conditions_short.append(
            (dataframe['volume'] > 0)
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
