import datetime
import json
import time

import pandas

import ChartAnalysis
import random
from threading import Thread
import TradingFront as tf
import TradingManager as tm
from logger import send_log_message as log

"""
this is what I call an analysis army. the army takes care of using the chart analyzers in large groups.
for example I need to fire a ruleset check on all 5m charts every 5 minutes, doing that is the job of 
the analysis army. 
the army creates a chart analyzer for each chart on each interval - these being the 'soldiers' and its
job, as mentioned previously is to manage them
"""

# try to load the 'trading_charts.txt' file
# in this file, a JSON expression that contains data on how to deal with certain charts.
# lists like - 'blocked charts' the list of charts that the program won't run a check on
# or the various interval lists which are lists of the charts that the program will be checking
# specific for each interval
try:
    trading_charts = json.load(open('trading_charts.txt', 'r'))
except Exception as e:
    print(e)
    trading_charts = {
        "blocked_charts": [],
        "interval_charts": {
            "5m": [],
            "15m": [],
            "30m": []
        }
    }

# we want to be able to control the army in another script, with the army being an instance so we
# make it a class.
class AnalysisArmy:

    # the profits will be documented in 'Bot Documentation/profits.txt' if true
    document_profits = False
    # the actions will be documented in 'Bot Documentation/actions.txt' if true
    document_actions = False

    # this is a json structure in which the chart analyzers will be stored, indexed by their interval and chart
    # for example to access the analyzer for the 15m EURUSD we call self.chart_analyzers['15m analyzers']['EURUSD']
    chart_analyzers = {}

    # initialize the army (in the current version - create the various chart analyzers)
    def initialize_army(self):

        log("Analysis Army: Initializing Army", False)

        self.chart_analyzers['5m analyzers'] = {}
        self.chart_analyzers['15m analyzers'] = {}
        self.chart_analyzers['30m analyzers'] = {}

        for c in ChartAnalysis.charts:
            self.chart_analyzers['5m analyzers'][c] = (ChartAnalysis.ChartAnalyzer(c, '5m'))
            self.chart_analyzers['15m analyzers'][c] = (ChartAnalysis.ChartAnalyzer(c, '15m'))
            self.chart_analyzers['30m analyzers'][c] = (ChartAnalysis.ChartAnalyzer(c, '30m'))

        log("Analysis Army: Army Initialized", False)

    # initiate a loop that is responsible for calling each unit check at the correct time.
    # it will call the trigger_check_in_unit function for the 5m charts every 5 minutes etc...
    def initiate_check_triggers(self):
        minutes = 0
        while True:
            if minutes % 5 == 0:
                Thread(target=self.trigger_check_in_unit, args=('5m',)).start()

            if minutes % 15 == 0:
                Thread(target=self.trigger_check_in_unit, args=('15m',)).start()

            if minutes % 30 == 0:
                Thread(target=self.trigger_check_in_unit, args=('30m',)).start()
            time.sleep(60)
            minutes += 1

    # run a ruleset check a certain interval unit
    def trigger_check_in_unit(self, interval):
        log('running a check on ' + interval + ' charts', False)
        blocked_list = trading_charts['blocked_charts']
        # go through the list of charts assigned to the specified interval and run the function
        # trigger_check_in_analyzer for each
        for c in trading_charts['interval_charts'][interval]:
            if c in blocked_list:
                log('Check is blocked for ' + c, False)
                continue
            self.trigger_check_in_analyzer(c, interval)

    # run a check in a specified analyzer and perform actions based on the output of the check
    def trigger_check_in_analyzer(self, chart, interval):
        id, data = self.chart_analyzers[interval + ' analyzers'][chart].check_ruleset()
        # id is 1 - open a buy position. data contains a json with the position data
        if id == 1:
            # tell the trading manager to open a position. True is returned if successful
            if tm.open_position(type='b', chart_name=chart, open_price=tf.get_available_money() * 0.01,
                                position_data=data):
                log('position opened: (buy) on ' + chart + '. details - ' + str(data), True)
                # document this action if needed
                if self.document_actions:
                    document = json.load(open('Bot Documentation/actions', 'w'))
                    try:
                        actions = document['actions']
                    except:
                        actions = []
                    actions.append('[' + datetime.datetime.now().strftime('%m/%d/%Y-%H:%M:%S') + '] ' +
                                   'position opened: (buy) on ' + chart + '. details - ' + str(data))
                    document['actions'] = actions
                    json.dump(actions, open('Bot Documentation/actions', 'w'))
            else:
                log('could not open position (buy) on ' + chart, True)
        # id is -1 - open a sell position. data contains a json with the position data
        elif id == -1:
            # tell the trading manager to open a position. True is returned if successful
            if tm.open_position(type='s', chart_name=chart, open_price=tf.get_available_money() * 0.01,
                                position_data=data):
                log('position opened: (sell) on ' + chart + '. details - ' + str(data), True)
                if self.document_actions:
                    document = json.load(open('Bot Documentation/actions', 'w'))
                    try:
                        actions = document['actions']
                    except:
                        actions = []
                    actions.append('[' + datetime.datetime.now().strftime('%m/%d/%Y-%H:%M:%S') + '] ' +
                                   'position opened: (sell) on ' + chart + '. details - ' + str(data))
                    document['actions'] = actions
                    json.dump(actions, open('Bot Documentation/actions', 'w'))
            else:
                log('could not open position (sell) on ' + chart, True)
        # id is -2 - close the position currently open on the specified chart
        elif id == -2:
            # try to close the position
            output = tm.close_position(chart_name=chart)
            # if the first variable of the output is True - successful
            if output[0]:
                log('position closed on ' + chart + '. profit: ' + str(output[1]), True)
                # document this action if needed
                if self.document_actions:
                    document = json.load(open('Bot Documentation/actions', 'w'))
                    try:
                        actions = document['actions']
                    except:
                        actions = []
                    actions.append('[' + datetime.datetime.now().strftime('%m/%d/%Y-%H:%M:%S') + '] ' +
                                   'position closed on ' + chart + '. profit: ' + str(output[1]))
                    document['actions'] = actions
                    json.dump(actions, open('Bot Documentation/actions', 'w'))
                # document the profit if needed
                if self.document_profits:
                    document = json.load(open('Bot Documentation/actions', 'r'))
                    try:
                        df = pandas.read_pickle("Bot Documentation/profits.pkl")
                    except:
                        df = pandas.DataFrame(columns=['datetime', 'profit', 'chart', 'interval', 'data'])

                    df.append({
                        'datetime': datetime.datetime.now().strftime('%m/%d/%Y-%H:%M:%S'),
                        'profit': str(output[1]),
                        'chart': chart,
                        'interval': interval,
                        'data': data
                    })

                    df.to_pickle("Bot Documentation/profits.pkl")
            else:
                log('could not close position on ' + chart, True)
        # id is 2 - update a position. The price crossed the take profit level and the analyzer decided that there's
        # an opportunity for making even more money. We update the position's details to make room for the profit to
        # grow even more
        elif id == 2:
            # tell the trading manager to update the position
            tm.update_position(chart, data)
            log('position updated on ' + chart + '. details - ' + str(data), True)
            # document this action if needed
            if self.document_actions:
                document = json.load(open('Bot Documentation/actions', 'r'))
                try:
                    actions = document['actions']
                except:
                    actions = []
                actions.append('[' + datetime.datetime.now().strftime('%m/%d/%Y-%H:%M:%S') + '] ' +
                               'position updated on ' + chart + '. details - ' + str(data))
                document['actions'] = actions
                json.dump(actions, open('Bot Documentation/actions', 'w'))
        # id is -10 - error
        elif id == -10:
            log('error trying to check ruleset in ' + chart + '-' + interval + ' :: ' + data, True)

    # pick a random analyzer instance
    def random_analyzer(self, interval=None):
        if (interval == None):
            return self.chart_analyzers[random.choice(['1m', '5m', '15m', '30m']) + ' analyzers'][random.choice(
                ChartAnalysis.charts)]
        else:
            return self.chart_analyzers[interval + ' analyzers'][random.choice(ChartAnalysis.charts)]

    # get a specified analyzer instance
    def get_analyzer(self, chart, interval):
        return self.chart_analyzers[interval + ' analyzers'][chart]

    # block a certain chart from trading on it
    def block_chart(self, chart):
        blocked = trading_charts['blocked']
        if chart in blocked:
            return 1
        blocked.append(chart)
        trading_charts['blocked'] = blocked
        json.dump(trading_charts, open('trading_charts.txt', 'w'))
        return 0

    # unblock a certain chart from trading on it
    def unblock_chart(self, chart):
        blocked = trading_charts['blocked']
        blocked.remove(chart)
        if chart not in blocked:
            return 1
        trading_charts['blocked'] = blocked
        json.dump(trading_charts, open('trading_charts.txt', 'w'))
        return 0

    # add a certain chart to an interval's list
    def add_chart_to_interval(self, chart, interval):
        try:
            interval_charts = trading_charts['interval_charts'][interval]
            if chart in interval_charts:
                return 1
            interval_charts.append(chart)
            trading_charts['interval_charts'][interval] = interval_charts
            json.dump(trading_charts, open('trading_charts.txt', 'w'))
            return 0
        except:
            return -1

    # remove a certain chart from an interval's list
    def remove_chart_from_interval(self, chart, interval):
        try:
            interval_charts = trading_charts['interval_charts'][interval]
            if chart not in interval_charts:
                return 1
            interval_charts.remove(chart)
            trading_charts['interval_charts'][interval] = interval_charts
            json.dump(trading_charts, open('trading_charts.txt', 'w'))
            return 0
        except:
            return -1
