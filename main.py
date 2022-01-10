import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import socket
import ChartAnalysis
from threading import Thread
import AnalysisArmy
import TradingManager as tm
from logger import send_log_message

"""
this is the main script. Run this to initialize the process (data manger needs to be run separately) 
"""

# create an army instance and cache it
army = AnalysisArmy.AnalysisArmy()

# initialize the army and start the trigger check loops
army.initialize_army()

Thread(target=army.initiate_check_triggers, args=()).start()


# this function starts a local server that will be used to communicate with the program during runtime through the
# client (called commander in this project)
# (this function will run as a thread)
def start_local_server():
    serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = 1000
    while True:
        try:
            serv.bind(('MY_IP', port))
            break
        except:
            port += 1

    send_log_message("Started local server on port: (" + str(port) + ")")
    serv.listen(100)
    serv.setblocking(True)
    while True:
        conn, addr = serv.accept()
        conn.send(str.encode("You are connected"))
        Thread(target=listen_to_commander, args=(conn, addr)).start()


# this function is a loop that continuously listens to signals from a commander and executes certain actions based on
# received commands
def listen_to_commander(conn, addr):
    while True:
        while True:
            try:
                data = conn.recv(4096).decode('utf-8')
                send_log_message('command received: ' + data)
                conn.send(str.encode(handle_command(data)))
            except:
                break

# this function is used by the local servers to handle commands. It gets a string input that contains the command
# splits it up to its segments, returns data and or executes an action based on what the command was if it's format
# is recogninized.
# for example: the command 'add_chart_to_interval EURUSD 5m' has 3 segments, this command is used to add a certain
# chart to a certain interval's list (this list contains the names of all charts the program will check when trading
# on a certain interval). For the command 'add_chart_to_interval' which is identified by looking at the first segment,
# the second segment, here being 'EURUSD', is expected to be a recognized chart name (which it is) and the third
# segment, here being '5m', is expected to be a recognized interval name (which it is)
def handle_command(command):
    command_segments = command.split(' ')

    if command_segments[0] == 'supported_charts':
        if len(command_segments) > 1:
            return 'is command has only one segment. No additional text needed.'
        st = ''
        for c in ChartAnalysis.charts:
            st += '\n' + c
        return st
    elif command_segments[0] == 'show_chart':
        if len(command_segments) > 3:
            return \
                "too many segments provided - expected 2-3 in the following form: " \
                "'show_chart (<chart name>-<interval>) (optionsl: [to show])]'"
        elif len(command_segments) < 2:
            return \
                "not enough segments provided - expected 2-3 in the following form: " \
                "'show_chart <chart name>-<interval> (optionsl: [to show])]'"
        chart_properties = command_segments[1].split('-')

        try:
            analyzer = army.get_analyzer(chart_properties[0], chart_properties[1])

            if len(command_segments) > 2:
                try:
                    indicators = command_segments[2]
                    analyzer.show_chart(
                        ma20=('MA20' in indicators),
                        ema20=('EMA20' in indicators),
                        ma50=('MA50' in indicators),
                        ema50=('EMA50' in indicators),
                        ma100=('MA100' in indicators),
                        ema100=('EMA100' in indicators),
                    )
                    return "showing chart: '" + command_segments[
                        1] + "'. \nto see available chart indicators run the command: show_available_chart_indicators "
                except Exception as e:
                    return "an error occurred while attempting to show chart: '" + command_segments[1] + "'" + str(e)
            else:
                try:
                    analyzer.show_chart()

                    return "showing chart: '" + command_segments[
                        1] + "'. \nto see available chart indicators run the command: show_available_chart_indicators"
                except Exception as e:
                    return "an error occurred while attempting to show chart: '" + command_segments[1] + "'" + str(e)
        except Exception as e:
            return "could not find a chart with the properties: '" + command_segments[1] + "'" + str(e)
    elif command_segments[0] == 'show_available_chart_indicators':
        if len(command_segments) > 1:
            return 'too many segments provided - expected 1'
        return '\nMA20\nEMA20\nMA50\nEMA50\nMA100\nEMA100'
    elif command_segments[0] == 'block':
        if len(command_segments) > 2:
            return "too many segments provided - expected 2 in the following form:" \
                   "block <chart name>"
        elif len(command_segments) < 2:
            return "not enough segments provided - expected 2 in the following form:" \
                   "block <chart name>"

        if command_segments[1] not in ChartAnalysis.charts:
            return "this chart name is not recognized"

        result = army.block_chart(command_segments[1])

        if result == 1:
            return 'this chart is already blocked' \
                   "\nuse the command 'blocked_charts' to display blocked charts" \
                   "\nuse the command 'unblock <chart_name>' to unblock a chart"

        return command_segments[1] + " is now blocked" \
                                     "\nuse the command 'blocked_charts' to display blocked charts" \
                                     "\nuse the command 'unblock <chart_name>' to unblock a chart"
    elif command_segments[0] == 'unblock':
        if len(command_segments) > 2:
            return "too many segments provided - expected 2 in the following form: '" \
                   "unblock <chart name>"
        elif len(command_segments) < 2:
            return "not enough segments provided - expected 2 in the following form: '" \
                   "unblock <chart name>'"

        if not command_segments[1] in ChartAnalysis.charts:
            return "this chart name is not recognized"

        result = army.block_chart(command_segments[1])

        if result == 1:
            return 'this chart is not blocked' \
                   "\nuse the command 'blocked_charts' to display blocked charts" \
                   "\nuse the command 'unblock <chart_name>' to unblock a chart"

        return command_segments[1] + " is no longer blocked" \
                                     "\nuse the command 'blocked_charts' to display blocked charts" \
                                     "\nuse the command 'block <chart_name>' to block a chart"
    elif command_segments[0] == 'blocked_charts':
        if len(command_segments) > 1:
            return "too many segments provided - expected 1"

        blocked_list = AnalysisArmy.trading_charts['blocked_charts']

        list_str = 'blocked charts:'
        for b in blocked_list:
            list_str += '\n' + b

        return list_str
    elif command_segments[0] == 'add_chart_to_interval':
        if len(command_segments) > 3:
            return "too many segments provided - expected 3 in the following form:" \
                   "add_chart_to_interval <chart name> <interval>"
        elif len(command_segments) < 3:
            return "not enough segments provided - expected 3 in the following form:" \
                   "add_chart_to_interval <chart name> <interval>"

        if command_segments[1] not in ChartAnalysis.charts:
            return "this chart name is not recognized"

        result = army.add_chart_to_interval(command_segments[1], command_segments[2])

        if result == 1:
            return "this chart is already in this interval's list" \
                   "\nuse the command 'interval_charts <interval>' to display charts in a interval" \
                   "\nuse the command 'remove_chart_from_interval <chart_name> <interval>' to remove a chart from a " \
                   "interval's list "
        elif result == -1:
            return "an error occurred while trying to add chart to this interval's list - make sure the interval name is correct"

        return command_segments[1] + " is now in the list of the interval - " + command_segments[2] + \
               "\nuse the command 'interval_charts <interval>' to display charts in a interval" \
               "\nuse the command 'remove_chart_from_interval <chart_name> <interval>' to remove a chart from a " \
               "interval's list "
    elif command_segments[0] == 'remove_chart_from_interval':
        if len(command_segments) > 3:
            return "too many segments provided - expected 3 in the following form:" \
                   "remove_chart_from_interval <chart name> <interval>"
        elif len(command_segments) < 3:
            return "not enough segments provided - expected 3 in the following form:" \
                   "remove_chart_from_interval <chart name> <interval>"

        if command_segments[1] not in ChartAnalysis.charts:
            return "this chart name is not recognized"

        result = army.remove_chart_from_interval(command_segments[1], command_segments[2])

        if result == 1:
            return "this chart is not in this interval's list" \
                   "\nuse the command 'interval_charts <interval>' to display charts in a interval" \
                   "\nuse the command 'add_chart_to_interval <chart_name> <interval>' to remove a chart from a " \
                   "interval's list "
        elif result == -1:
            return "an error occurred while trying to remove chart from this interval's list - make sure the interval name is correct"

        return "removed " + command_segments[1] + " from the list of the interval - " + command_segments[2] + \
               "\nuse the command 'interval_charts <interval>' to display charts in a interval" \
               "\nuse the command 'add_chart_to_interval <chart_name> <interval>' to remove a chart from a " \
               "interval's list "
    elif command_segments[0] == 'interval_charts':
        if len(command_segments) > 2:
            return "too many segments provided - expected 2 in the following form:" \
                   "interval_charts <interval>"
        if len(command_segments) < 2:
            return "not enough segments provided - expected 2 in the following form:" \
                   "interval_charts <interval>"

        try:
            interval_charts = AnalysisArmy.trading_charts['interval_charts'][command_segments[1]]

            list_str = 'charts of the interval ' + command_segments[1] + ':'
            for c in interval_charts:
                list_str += '\n' + c

            return list_str
        except:
            return "an error occurred while trying to get this interval's chart list - make sure the interval name " \
                   "is correct"
    elif command_segments[0] == 'close_position':
        if len(command_segments) > 2:
            return "too many segments provided - expected 2 in the following form:" \
                   "close_position <chart_name>"
        if len(command_segments) < 2:
            return "not enough segments provided - expected 2 in the following form:" \
                   "close_position <chart_name>"

        output = tm.close_position(chart_name=command_segments[1])
        if output[0]:
            return ('position closed on ' + command_segments[1] + '. profit: ' + str(output[1]), True)
        else:
            return ('could not close position on ' + command_segments[1], True)
    elif command_segments[0] == 'report_closed':
        if len(command_segments) > 2:
            return "too many segments provided - expected 2 in the following form:" \
                   "report_closed <chart_name>"
        if len(command_segments) < 2:
            return "not enough segments provided - expected 2 in the following form:" \
                   "report_closed <chart_name>"

        try:
            tm.report_closed(chart_name=command_segments[1])
            return "position at " + command_segments[1] + " is now considered closed"
        except:
            return "could not close position for " + command_segments[1] + " is that a supported chart name? " \
                                                                           "\n use the command 'supported_charts' to " \
                                                                           "see the names of all charts supported by " \
                                                                           "this software "

    return "'" + command_segments[0] + "' is not recognized as a valid command."

Thread(target=start_local_server, args=()).start()
