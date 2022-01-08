import json
import TradingFront as tf

"""
the trading manager is the script that manages the trading actions inside the program, one step before the trading
front that manages the actual trading.
to open, close or update a position, this scripts methods are called, those than call the trading front's methods.
it is responsible for verifying, documenting, and keeping track of all trading actions, before the trading front is
said to do so. 
"""

try:
    trading_doc = json.load(open('trading_doc.txt', 'r'))
except:
    trading_doc = {
        'open_positions': {}
    }

closed_position_data = {
                'position_open': 0,
                'open_position': {
                    'type': '',
                    'open_value': 0,
                    'stop_loss': 0,
                    'stop_profit': 0.0,
                    'intervals_open': 0,
                    'reward_to_risk': 0.0
                },
                'opened_positions': []
            }

def open_position(type='', chart_name='', open_price=100, position_data=None):
    if position_data is None:
        position_data = closed_position_data
    if tf.open_position(type, chart_name, open_price):
        open_positions = trading_doc['open_positions']
        open_positions[chart_name] = position_data
        trading_doc['open_positions'] = open_positions
        json.dump(trading_doc, open('trading_doc.txt', 'w'))
        return True
    return False

def update_position(chart_name='', position_data=None):
    open_positions = trading_doc['open_positions']
    open_positions[chart_name] = position_data
    trading_doc['open_positions'] = open_positions
    json.dump(trading_doc, open('trading_doc.txt', 'w'))

def close_position(chart_name):
    profit = tf.close_position(chart_name)
    if  profit != 'ERROR':
        open_positions = trading_doc['open_positions']
        open_positions[chart_name] = closed_position_data
        trading_doc['open_positions'] = open_positions
        json.dump(trading_doc, open('trading_doc.txt', 'w'))
        return True, profit
    return (False,)

def report_closed(chart_name):
    open_positions = trading_doc['open_positions']
    open_positions[chart_name] = closed_position_data
    trading_doc['open_positions'] = open_positions
    json.dump(trading_doc, open('trading_doc.txt', 'w'))


def get_position_data(chart_name):
    try:
        trading_doc = json.load(open('trading_doc.txt', 'r'))
        return trading_doc['open_positions'][chart_name]
    except:
        return closed_position_data
