import math
from scipy.signal import savgol_filter


def calculate_avg(values):
    a = []
    for i in range(len(values)):
        a.append(sum(values[0:i]) / (i + 1))

    return a


def calculate_avg_value(values):
    return sum(values) / len(values)


def calculate_ma(values, samples):
    ma = []

    for i in range(samples, len(values)):
        ma.append(sum(values[i - samples:i]) / samples)

    return ma


def calculate_ema(values, samples):
    ema = []

    k = (2 / (samples + 1))

    ema.append(sum(values[0:samples]) / samples)

    for i in range(samples + 1, len(values)):
        ema.append((values[i] * k) + (ema[i - 1 - samples] * (1 - k)))

    return ema


def calculate_chart_movement(candle_sticks=[]):
    return [(c['close'] + c['open'] + c['high'] + c['low']) / 4 for c in candle_sticks]


def calculate_tr(candle_sticks=[]):
    tr = []
    for i in range(1, len(candle_sticks)):
        tr.append(max([candle_sticks[i]['high'] - candle_sticks[i]['low'],
                       candle_sticks[i]['high'] - candle_sticks[i - 1]['close'],
                       candle_sticks[i - 1]['close'] - candle_sticks[i]['low']
                       ]))
    return tr


def calculate_atr(candle_sticks=[], period=7):
    tr = []
    atr = []
    for i in range(1, len(candle_sticks)):
        tr.append(max([candle_sticks[i]['high'] - candle_sticks[i]['low'],
                       candle_sticks[i]['high'] - candle_sticks[i - 1]['close'],
                       candle_sticks[i - 1]['close'] - candle_sticks[i]['low']
                       ]))
        if i >= period:
            atr.append(sum(tr[i - period:i]) / period)
    return atr


def calculate_macd(values, fast_period=12, slow_period=26, signal=9):
    fast = calculate_ema(values, fast_period)
    slow = calculate_ema(values, slow_period)

    macd = []
    for i in range(len(slow) - 1, 0, -1):
        macd.append(fast[len(fast) - i] - slow[len(slow) - i])

    return macd, calculate_ema(macd, signal)


def calculate_stochastic(values=[], lows=[], highs=[], window=14, k_smooth=3, d_smooth=3):
    assert len(values) == len(lows) == len(highs)

    s = []
    for v in range(window, len(lows)):
        mx = max(highs[v - window: v + 1])
        mn = min(lows[v - window: v + 1])
        if mn == mx:
            s.append(0.5)
        else:
            s.append((values[v] - mn) / (mx - mn))

        k = calculate_ma(s, k_smooth)
        d = calculate_ma(k, d_smooth)
    return k, d


def calculate_supertrend(candle_sticks=[], period=7, multiplayer=3):
    tr = []
    b_upper = []
    b_lower = []
    f_upper = []
    f_lower = []
    super_trend_bands = []
    super_trend_trends = []
    for i in range(1, len(candle_sticks)):
        tr.append(max([candle_sticks[i]['high'] - candle_sticks[i]['low'],
                       candle_sticks[i]['high'] - candle_sticks[i - 1]['close'],
                       candle_sticks[i - 1]['close'] - candle_sticks[i]['low']
                       ]))
        if i >= period:
            atr = sum(tr[i - period:i]) / period
            b_upper.append(
                ((candle_sticks[i]['high'] + candle_sticks[i]['low']) / 2) +
                (multiplayer * atr)
            )
            b_lower.append(
                ((candle_sticks[i]['high'] + candle_sticks[i]['low']) / 2) -
                (multiplayer * atr)
            )
            if i == period:
                f_upper.append(b_upper[i - period])
                f_lower.append(b_lower[i - period])
                super_trend_bands.append(b_upper[i - period])
                super_trend_trends.append(-1)
            elif i > period:
                f_upper.append(
                    b_upper[i - period]
                    if (b_upper[i - period] < f_upper[i - period - 1] or
                        candle_sticks[i - 1]['close'] > f_upper[i - period - 1])
                    else f_upper[i - period - 1]
                )

                f_lower.append(
                    b_lower[i - period]
                    if (b_lower[i - period] > f_lower[i - period - 1] or
                        candle_sticks[i - 1]['close'] < f_lower[i - period - 1])
                    else f_lower[i - period - 1]
                )

                if super_trend_bands[i - period - 1] == f_upper[i - period - 1]:
                    if candle_sticks[i]['close'] > f_upper[i - period]:
                        super_trend_bands.append(f_lower[i - period])
                        super_trend_trends.append(1)
                    else:
                        super_trend_bands.append(f_upper[i - period])
                        super_trend_trends.append(-1)
                elif super_trend_bands[i - period - 1] == f_lower[i - period - 1]:
                    if candle_sticks[i]['close'] > f_lower[i - period]:
                        super_trend_bands.append(f_lower[i - period])
                        super_trend_trends.append(1)
                    else:
                        super_trend_bands.append(f_upper[i - period])
                        super_trend_trends.append(-1)

    return super_trend_bands, super_trend_trends


def to_haikin_ahi(candle_sticks):
    ha_close = (candle_sticks[1]['close'] + candle_sticks[1]['open'] +
                candle_sticks[1]['high'] + candle_sticks[1]['low']) / 4
    ha_open = (candle_sticks[0]['close'] + candle_sticks[0]['open']) / 2
    heikin_ashi = [
        {
            'close': ha_close,
            'open': ha_open,
            'high': max([candle_sticks[0]['high'], ha_open, ha_close]),
            'low': min([candle_sticks[0]['low'], ha_open, ha_close])
        }
    ]
    for i in range(2, len(candle_sticks)):
        ha_close = (candle_sticks[i]['close'] + candle_sticks[i]['open'] +
                    candle_sticks[i]['high'] + candle_sticks[i]['low']) / 4
        ha_open = (candle_sticks[i - 1]['close'] + candle_sticks[i - 1]['open']) / 2
        heikin_ashi.append(
            {
                'close': ha_close,
                'open': ha_open,
                'high': max([candle_sticks[i - 1]['high'], ha_open, ha_close]),
                'low': min([candle_sticks[i - 1]['low'], ha_open, ha_close])
            }
        )

    return heikin_ashi


def calculate_integral(function_values, delta_x=1):
    integral = [0]

    for i in range(len(function_values)):
        integral.append(integral[i] + (function_values[i] * delta_x))

    return integral[1:]


def average_line(function_values):
    avg = []
    for f in range(len(function_values[0])):
        sum = 0
        for i in range(len(function_values)):
            sum += function_values[i][f]
        avg.append(sum / len(function_values))
    return avg


def calculate_sunshine(values, period1=20, period2=50, period3=100):
    assert period1 < period2 < period3

    ema1 = savgol_filter(calculate_ema(values, period1), 53, 3)
    ema2 = savgol_filter(calculate_ema(values, period2), 53, 3)
    ema3 = savgol_filter(calculate_ema(values, period3), 53, 3)

    sunshine = []
    cross1_2 = 0
    cross2_3 = 0
    for i in range(len(ema3), 1, -1):
        if (sign(ema1[len(ema1) - i] - ema2[len(ema2) - i]) !=
                sign(ema1[len(ema1) - i - 1] - ema2[len(ema2) - i - 1])):
            cross1_2 = i
        if (sign(ema2[len(ema2) - i] - ema3[len(ema3) - i]) !=
                sign(ema2[len(ema2) - i - 1] - ema3[len(ema3) - i - 1])):
            cross2_3 = i
        if cross1_2 > cross2_3:
            sunshine.append((cross2_3 - i) / (cross1_2 - cross2_3))
        else:
            sunshine.append(0)
    return sunshine

def calculate_derivative(function_values, delta_x=1, smoothness=1):
    assert delta_x > 0
    assert smoothness > 0

    derivative = [0] * (smoothness + 1)

    for i in range(1, len(function_values)):
        derivative.append((function_values[i] - function_values[i - smoothness]) / delta_x)

    derivative.extend([derivative[-1]] * (len(function_values) - len(derivative)))

    return derivative


def fit_to_range(values, mininimum_value, maximum_value, fit_start=0, fit_end=-1, anchor_point=None):
    min_val = min(values[fit_start:fit_end])
    max_val = max(values[fit_start:fit_end])

    if (max_val - min_val == 0):
        return values

    fit_values = []

    if anchor_point is not None:
        assert mininimum_value < anchor_point < maximum_value
        for v in values:
            if v > anchor_point:
                fit_values.append(
                    (((v - anchor_point) / (max_val - anchor_point)) * (maximum_value - anchor_point)) + anchor_point)
            else:
                fit_values.append(
                    (((v - min_val) / (anchor_point - min_val)) * (anchor_point - mininimum_value)) + mininimum_value)

        return fit_values

    for v in values:
        fit_values.append((((v - min_val) / (max_val - min_val)) * (maximum_value - mininimum_value)) + mininimum_value)

    return fit_values


def fit_range_of_value_lists(to_fit, fit_to, fit_start=0, fit_end=-1, anchor_point=None):
    return fit_to_range(to_fit, min(fit_to), max(fit_to), fit_start, fit_end, anchor_point)


def error_between_two_value_lists(to_check, check_relative_to):
    sum = 0

    for i in range(len(to_check)):
        sum += abs(check_relative_to[i] - to_check[i])

    return sum / len(to_check)


def sign(val):
    if val > 0:
        return 1
    elif val < 0:
        return -1
    else:
        return 0


def keep_in_range(val, min=0, max=1):
    if type(val) is list:
        return [keep_in_range(v) for v in val]
    return (val + ((max - val) * (val > max)) + ((min - val) * (val < min)))
