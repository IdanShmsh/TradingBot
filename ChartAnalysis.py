import os
import pandas
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import math
import GraphCalculator
import finplot as fplt
from scipy.signal import savgol_filter
import TradingManager as tm

"""
the chart analysis is the heart of this whole program, here runs all the logic that lets this bot, hopefully, be
profitable.
the job of the chart analyzer is to look at the current data, analyze it, and decide on the actions the bot should
take.

currently the analyzer is using only a method of algorithmic trading, using only a specific ruleset it determines where
and when to enter and exit the market. current rule set at use is my own 'sunshine strategy' all the information on it
is in 'Docs/Ruleset-sunshine.txt'
I am working on integrating a certain ai model to be a part of the analysis process
"""

charts = [
    'EURUSD',
    'EURGBP',
    'EURAUD',
    'EURNZD',
    'EURCAD',
    'EURCHF',
    'GBPUSD',
    'AUDUSD',
    'NZDUSD',
    'USDCAD',
    'USDCHF',
    'USDJPY',
    'AUDCAD',
    'AUDCHF',
    'AUDJPY',
    'AUDNZD',
    'CADCHF',
    'CADJPY',
    'CHFJPY',
    'EURJPY',
    'GBPAUD',
    'GBPCAD',
    'GBPCHF',
    'GBPJPY',
    'GBPNZD',
    'NZDCAD',
    'NZDCHF',
    'NZDJPY',
    'USDSGD',
    'AUDSGD',
    'EURSGD',
    'GBPSGD',
    'CHFDKK',
    'CHFSEK',
    'EURDKK',
    'EURNOK',
    'EURPLN',
    'EURSEK',
    'EURZAR',
    'GBPDKK',
    'GBPNOK',
    'GBPSEK',
    'GBPZAR',
    'USDCNH',
    'USDDKK',
    'USDHKD',
    'USDMXN',
    'USDNOK',
    'USDPLN',
    'USDSEK',
    'USDZAR',
    'SGDJPY',
    'DKKNOK',
    'SEKNOK',
]

"""
no need to mention why it's a class
"""
class ChartAnalyzer:


    def __init__(self, chart_name, interval, show_loaded_chart_data=False, load_new_network=False):
        self.chart_name = chart_name
        self.interval = interval

        self.load_data(show_chart=show_loaded_chart_data)

    # load the data of this chart.
    def load_data(self, show_chart=False):
        # locate the relevant pickle file created by the chart data manager and load the data from it
        self.data = pandas.read_pickle("Chart_Data_Files/" + self.chart_name + "-" + self.interval + ".pkl")

        # convert the data frame to a list
        temp = self.data.values.tolist()
        self.data_values = [val for sublist in temp for val in sublist]

        self.candle_stick_count = 0
        self.network_data_length = 0
        self.network_data_set_length = 0
        self.candle_sticks = []
        self.heikin_ashi = []
        self.closing_prices = []
        self.opening_prices = []
        self.low_prices = []
        self.high_prices = []

        # create the array of candlesticks where each is a json with the indexes 'open,close,high,low' being the
        # values of the parameters of the candlestick
        # also create the lists of each of these parameters separately
        for i in range(math.floor(len(self.data_values) / 4)):
            self.candle_sticks.append(
                {
                    'open': float(self.data_values[(4 * i)]),
                    'close': float(self.data_values[(4 * i) + 3]),
                    'high': float(self.data_values[(4 * i) + 1]),
                    'low': float(self.data_values[(4 * i) + 2])
                }
            )

            self.closing_prices.append(self.candle_sticks[i]['close'])
            self.opening_prices.append(self.candle_sticks[i]['open'])
            self.low_prices.append(self.candle_sticks[i]['low'])
            self.high_prices.append(self.candle_sticks[i]['high'])

        # generate the heikin ashi candlestick list
        self.heikin_ashi = GraphCalculator.to_haikin_ahi(self.candle_sticks)

        # generate the various moving averages and apply a savgol filter (51, 3) to each
        self._10MA = savgol_filter(GraphCalculator.calculate_ma(self.closing_prices, 10), 51, 3)
        self._10EMA = savgol_filter(GraphCalculator.calculate_ema(self.closing_prices, 10), 51, 3)
        self.__20MA = savgol_filter(GraphCalculator.calculate_ma(self.closing_prices, 20), 51, 3)
        self.__20EMA = savgol_filter(GraphCalculator.calculate_ema(self.closing_prices, 20), 51, 3)
        self._50MA = savgol_filter(GraphCalculator.calculate_ma(self.closing_prices, 50), 51, 3)
        self._50EMA = savgol_filter(GraphCalculator.calculate_ema(self.closing_prices, 50), 51, 3)
        self._100MA = savgol_filter(GraphCalculator.calculate_ma(self.closing_prices, 100), 51, 3)
        self._100EMA = savgol_filter(GraphCalculator.calculate_ema(self.closing_prices, 100), 51, 3)
        self._150MA = savgol_filter(GraphCalculator.calculate_ma(self.closing_prices, 150), 51, 3)
        self._150EMA = savgol_filter(GraphCalculator.calculate_ema(self.closing_prices, 150), 51, 3)
        self._200MA = savgol_filter(GraphCalculator.calculate_ma(self.closing_prices, 200), 51, 3)
        self._200EMA = savgol_filter(GraphCalculator.calculate_ema(self.closing_prices, 200), 51, 3)

        # generate the macd fast and slow lines (on default parameters)
        self.macd_fast, self.macd_slow = GraphCalculator.calculate_macd(self.closing_prices)

        #apply a savgol filter to each
        self.macd_fast = savgol_filter(self.macd_fast, 51, 3)
        self.macd_slow = savgol_filter(self.macd_slow, 51, 3)

        #generate a stochastic oscilator
        self.stochastic_K, self.stochastic_D = \
            GraphCalculator.calculate_stochastic(self.closing_prices, self.low_prices, self.high_prices, 14)

        # generate a super trend
        self.super_trend_bands, self.super_trend_trends = GraphCalculator.calculate_supertrend(self.candle_sticks)

        # generate a sunshine indicator
        self.sunshine = GraphCalculator.calculate_sunshine(self.closing_prices)

    # check the ruleset
    def check_ruleset(self, candlestick=0, load_data=True):
        if load_data:
            try:
                self.load_data()
            except Exception as e:
                return 10, 'error trying to load data' + str(e).split('\n')[-2]
        # cache the current closing price (just because it will be accessed alot)
        current_close_price = self.closing_prices[len(self.closing_prices) - candlestick - 1]
        position_data = tm.get_position_data(self.chart_name)
        # check the following ruleset if the analyzer is 1m or 5m

        #
        if self.interval == '15m' or self.interval == '5m' or self.interval == '30m':
            # if there's an open position currently
            if position_data['position_open'] == 1:
                # if a position is open on this chart but the interval is not this analyzer's interval, retrun
                if position_data['open_position']['interval'] != self.interval:
                    return 0, None
                # follow these rules when the current open position is a long position (buy)
                if position_data['open_position']['type'] == 'b':
                    # if the market closed bellow the stop loss - close the position
                    if (current_close_price < position_data['open_position']['stop_loss'] or
                            (self.super_trend_trends[len(self.super_trend_trends) - candlestick - 1] <= 0)):
                        # close the position
                        return -2, position_data['open_position']
                    # if the market closed above the stop profit - update position to higher values ride trend
                    # move stop loss to half-way between the current closing price and previous open value
                    # move the open value to the current closing price
                    # reward to risk stays 1.5
                    elif current_close_price > position_data['open_position']['stop_profit']:
                        if (self.macd_fast[len(self.macd_fast) - candlestick - 1] < 0 or
                                self.macd_slow[len(self.macd_slow) - candlestick - 1] >
                                self.macd_fast[len(self.macd_fast) - candlestick - 1]):
                            return -2, position_data['open_position']

                        min_close = min(self.closing_prices[
                                        len(self.closing_prices) - candlestick - 2 -
                                        position_data['open_position']['intervals_open']:
                                        len(self.closing_prices) - candlestick - 1])

                        if ((abs(position_data['open_position']['open_value'] - position_data['open_position'][
                            'stop_loss']) == 0)):
                            return -2, position_data['open_position']

                        stoploss_co = abs((position_data['open_position']['stop_loss'] - min_close) /
                                          (position_data['open_position']['open_value'] -
                                           position_data['open_position'][
                                               'stop_loss']))

                        position_data = self.get_position_data(
                            open_value=current_close_price,
                            type='b',
                            stop_loss=(current_close_price -
                                       (abs(current_close_price - position_data['open_position'][
                                           'open_value']) * stoploss_co)),
                            reward_to_risk=1
                        )
                        return 2, position_data

                # follow these rules when the current open position is a short position (sell)
                else:
                    # if the market closed above the stop loss - close the position
                    if ((current_close_price > position_data['open_position']['stop_loss']) or
                            (self.super_trend_trends[len(self.super_trend_trends) - candlestick - 1] >= 0)):
                        # close the position
                        return -2, position_data['open_position']
                    # if the market closed blow the stop profit - update position to lower values - ride trend
                    # move stop loss to half-way between the current closing price and previous open value
                    # move the open value to the current closing price
                    # reward to risk stays 1.5
                    elif current_close_price < position_data['open_position']['stop_profit']:
                        if (self.macd_fast[len(self.macd_fast) - candlestick - 1] > 0 or
                                self.macd_slow[len(self.macd_slow) - candlestick - 1] <
                                self.macd_fast[len(self.macd_fast) - candlestick - 1]):
                            return -2, position_data['open_position']

                        max_close = max(self.closing_prices[
                                        len(self.closing_prices) - candlestick - 2 -
                                        position_data['open_position']['intervals_open']:
                                        len(self.closing_prices) - candlestick - 1])

                        if abs(position_data['open_position']['open_value'] - position_data['open_position'][
                            'stop_loss']) == 0:
                            return -2, position_data['open_position']

                        stoploss_co = abs((position_data['open_position']['stop_loss'] - max_close) /
                                          (position_data['open_position']['open_value'] -
                                           position_data['open_position'][
                                               'stop_loss']))

                        position_data = self.get_position_data(
                            open_value=current_close_price,
                            type='s',
                            stop_loss=(current_close_price +
                                       (abs(position_data['open_position']['open_value'] -
                                            current_close_price) * stoploss_co)),
                            reward_to_risk=1
                        )
                        return 2, position_data

                return 0.5, None

            else:  # if there is no position opened currently - look for an enter
                # 20 EMA is above 50 EMA which is above 100 EMA - trending up, look for a long
                # enter (buy)
                if (self._10EMA[len(self._10EMA) - candlestick - 1] > self._50EMA[len(self._50EMA) - candlestick - 1]
                        > self._100EMA[len(self._100EMA) - candlestick - 1]):

                    # check that the super trend indicator agrees with the bearish trend
                    if self.super_trend_trends[len(self.super_trend_trends) - candlestick - 1] <= 0:
                        return 0, None
                    if (self.super_trend_bands[len(self.super_trend_bands) - candlestick - 1] <
                            self._100EMA[len(self._100EMA) - candlestick - 1]):
                        return 0, None

                    # check that current close is bigger than previous close, both are above the 10EMA
                    # both candles before are below it
                    if not ((self.closing_prices[len(self.closing_prices) - candlestick - 1] >
                             self.closing_prices[len(self.closing_prices) - candlestick - 2]) and
                            (self.closing_prices[len(self.closing_prices) - candlestick - 1] >
                             self._10EMA[len(self._10EMA) - candlestick - 1]) and
                            (self.closing_prices[len(self.closing_prices) - candlestick - 2] >
                             self._10EMA[len(self._10EMA) - candlestick - 2]) and
                            (self.closing_prices[len(self.closing_prices) - candlestick - 3] <
                             self._10EMA[len(self._10EMA) - candlestick - 3]) and
                            (self.closing_prices[len(self.closing_prices) - candlestick - 4] <
                             self._10EMA[len(self._10EMA) - candlestick - 4])):
                        return 0, None

                    # check that the current and previous heikin ashi candlestick are green candles
                    current_heikin_ashi_candle = self.heikin_ashi[len(self.heikin_ashi) - candlestick - 1]
                    prev_heikin_ashi_candle = self.heikin_ashi[len(self.heikin_ashi) - candlestick - 2]
                    if not ((current_heikin_ashi_candle['close'] > current_heikin_ashi_candle['open'])):
                        return 0, None

                    # check that the fast macd indicator is positive
                    if not (self.macd_fast[len(self.macd_fast) - candlestick - 1] > 0 and
                            (self.macd_fast[len(self.macd_fast) - candlestick - 1] -
                             self.macd_fast[len(self.macd_fast) - candlestick - 2] >= 0)):
                        return 0, None

                    if self.sunshine[len(self.sunshine) - candlestick - 1] < 0.5:
                        return 0, None

                    # great! current market's state fits the conditions we're looking for to place a long position

                    # get the position data and return
                    position_data = self.get_position_data(
                        open_value=current_close_price,
                        type='b',
                        stop_loss=(current_close_price + self._50EMA[len(self._50EMA) - candlestick - 1]) / 2,
                        reward_to_risk=1.5
                    )
                    return 1, position_data

                # 20 EMA is below 50 EMA which is below 100 EMA - trending down, look for a short enter (sell)
                elif self._10EMA[len(self._10EMA) - candlestick - 1] < self._50EMA[len(self._50EMA) - candlestick - 1] \
                        < self._100EMA[len(self._100EMA) - candlestick - 1]:

                    # check that the super trend indicator agrees with the bearish trend
                    if self.super_trend_trends[len(self.super_trend_trends) - candlestick - 1] >= 0:
                        return 0, None
                    if (self.super_trend_bands[len(self.super_trend_bands) - candlestick - 1] >
                            self._100EMA[len(self._100EMA) - candlestick - 1]):
                        return 0, None

                    # check that current close is lower than previous close, both are below the 10EMA
                    # both candles before are above it
                    if not ((self.closing_prices[len(self.closing_prices) - candlestick - 1] <
                             self.closing_prices[len(self.closing_prices) - candlestick - 2]) and
                            (self.closing_prices[len(self.closing_prices) - candlestick - 1] <
                             self._10EMA[len(self._10EMA) - candlestick - 1]) and
                            (self.closing_prices[len(self.closing_prices) - candlestick - 2] <
                             self._10EMA[len(self._10EMA) - candlestick - 2]) and
                            (self.closing_prices[len(self.closing_prices) - candlestick - 3] >
                             self._10EMA[len(self._10EMA) - candlestick - 3]) and
                            (self.closing_prices[len(self.closing_prices) - candlestick - 4] >
                             self._10EMA[len(self._10EMA) - candlestick - 4])):
                        return 0, None

                    # check that the current and previous heikin ashi candlestick are red candles
                    current_heikin_ashi_candle = self.heikin_ashi[len(self.heikin_ashi) - candlestick - 1]
                    prev_heikin_ashi_candle = self.heikin_ashi[len(self.heikin_ashi) - candlestick - 2]
                    if not ((current_heikin_ashi_candle['close'] < current_heikin_ashi_candle['open'])):
                        return 0, None

                    # check that the fast macd indicator is negative
                    if not (self.macd_fast[len(self.macd_fast) - candlestick - 1] < 0 and
                            (self.macd_fast[len(self.macd_fast) - candlestick - 1] <
                             self.macd_fast[len(self.macd_fast) - candlestick - 2])):
                        return 0, None

                    if self.sunshine[len(self.sunshine) - candlestick - 1] < 0.5:
                        return 0, None

                    # great! current market's state fits the conditions we're looking for to place a short position

                    # get the pip for this chart real quick
                    pip = 0.01 if self.chart_name[3:] == 'JPY' else 0.0001
                    # get the position data and return
                    position_data = self.get_position_data(
                        open_value=current_close_price,
                        type='s',
                        stop_loss=(current_close_price + self._50EMA[len(self._50EMA) - candlestick - 1]) / 2,
                        reward_to_risk=1.5
                    )
                    return -1, position_data
        return (0, None)

    # turn the parameters to a correctly formatted json containing the position data
    def get_position_data(self, open_value, type, stop_loss, reward_to_risk=1.5):
        position_data = {}
        position_data['position_open'] = 1
        position_data['open_position'] = {}
        position_data['open_position']['type'] = type
        position_data['open_position']['open_value'] = open_value
        position_data['open_position']['stop_loss'] = stop_loss
        position_data['open_position']['stop_profit'] = open_value + (reward_to_risk * (open_value - stop_loss))
        position_data['open_position']['intervals_open'] = 0
        position_data['open_position']['reward_to_risk'] = reward_to_risk
        position_data['open_position']['interval'] = self.interval
        return position_data

    # show the chart (using finplot)
    def show_chart(self,
                   ma20=False,
                   ema20=False,
                   ma50=False,
                   ema50=False,
                   ma100=False,
                   ema100=False,
                   ma200=False,
                   ema200=False):

        self.load_data()

        ax, ax2 = fplt.create_plot(self.chart_name, rows=2)

        fplt.candlestick_ochl(self.data[['Open', 'Close', 'High', 'Low']], ax)

        if ma20:
            to_plot = ([self._10MA[0]] * 20)
            to_plot.extend(self._10MA)
            fplt.plot(to_plot, ax=ax, color='#009', legend='ma-20')

        if ema20:
            to_plot = ([self._10EMA[0]] * 20)
            to_plot.extend(self._10EMA)
            fplt.plot(to_plot, ax=ax, color='#00f', legend='ema-20')

        if ma50:
            to_plot = ([self._50MA[0]] * 50)
            to_plot.extend(self._50MA)
            fplt.plot(to_plot, ax=ax, color='#090', legend='ma-50')

        if ema50:
            to_plot = ([self._50EMA[0]] * 50)
            to_plot.extend(self._50EMA)
            fplt.plot(to_plot, ax=ax, color='#0f0', legend='ema-50')

        if ma100:
            to_plot = ([self._100MA[0]] * 100)
            to_plot.extend(self._100MA)
            fplt.plot(to_plot, ax=ax, color='#900', legend='ma-100')

        if ema100:
            to_plot = ([self._100EMA[0]] * 100)
            to_plot.extend(self._100EMA)
            fplt.plot(to_plot, ax=ax, color='#f00', legend='ema-100')

        if ma200:
            to_plot = ([self._200MA[0]] * 200)
            to_plot.extend(self._200MA)
            fplt.plot(to_plot, ax=ax, color='#900', legend='ma-200')

        if ema200:
            to_plot = ([self._200EMA[0]] * 200)
            to_plot.extend(self._200EMA)
            fplt.plot(to_plot, ax=ax, color='#f00', legend='ema-200')

        to_plot = ([self.super_trend_bands[0]] * (len(self.closing_prices) - len(self.super_trend_bands)))
        to_plot.extend(self.super_trend_bands)
        fplt.plot(to_plot, ax=ax, color='#f00', legend='supertrends')

        to_plot = [.5] * (len(self.closing_prices) - len(self.stochastic_K))
        to_plot.extend(self.stochastic_K)
        fplt.plot(to_plot, ax=ax2, color='#00f', legend='stochastics_K')

        to_plot = [.5] * (len(self.closing_prices) - len(self.stochastic_D))
        to_plot.extend(self.stochastic_D)
        fplt.plot(to_plot, ax=ax2, color='#f00', legend='stochastics_D')

        fplt.plot([1] * len(self.closing_prices), ax=ax2, color='#000')
        fplt.plot([0] * len(self.closing_prices), ax=ax2, color='#000')
        fplt.plot([0.2] * len(self.closing_prices), ax=ax2, color='#0ff')
        fplt.plot([0.8] * len(self.closing_prices), ax=ax2, color='#0ff')

        fplt.show()
