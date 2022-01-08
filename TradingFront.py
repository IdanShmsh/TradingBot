import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

"""
the trading front is the script that takes care of actually making actions such as opening and closing positions
on the trading platform of choice, as well as doing stuff such as checking the amount of available money 
on this platform

in this current version, due to me not wanting to use an api, i went all crazy doing it the hard way, using selenium
(a package that lets a python code to perform interactions with a web browser in my case - Chrome), i interact
with the website of my platform of choice 'plus500' to do the stuff mentioned above.

[[this can all be changed very easily to another method]]
"""

# this json contains the xpaths for all action buttons of each chart
# THIS IS COMPLIANT ONLY WITH MY LAYOUT
chart_buttons_xpaths = {
    'EURUSD': {
        'sell': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[1]/div[4]/button',
        'buy': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[1]/div[6]/button',
        'close': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[1]/div['
                 '12]/div/div/span[2]/button',
        'profit': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[1]/div['
                  '12]/div/div/span[1]/strong[2]/span[2]',
    },
    'USDJPY': {
        'sell': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[2]/div[4]/button',
        'buy': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[2]/div[6]/button',
        'close': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[2]/div['
                 '12]/div/div/span[2]/button',
        'profit': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[2]/div['
                  '12]/div/div/span[1]/strong[2]/span[2]'
    },
    'GBPUSD': {
        'sell': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[3]/div[4]/button',
        'buy': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[3]/div[6]/button',
        'close': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[3]/div['
                 '12]/div/div/span[2]/button',
        'profit': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[3]/div['
                  '12]/div/div/span[1]/strong[2]/span[2]'
    },
    'AUDUSD': {
        'sell': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[4]/div[4]/button',
        'buy': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[4]/div[6]/button',
        'close': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[4]/div['
                 '12]/div/div/span[2]/button',
        'profit': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[4]/div['
                  '12]/div/div/span[1]/strong[2]/span[2]'
    },
    'USDCAD': {
        'sell': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[5]/div[4]/button',
        'buy': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[5]/div[6]/button',
        'close': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[5]/div['
                 '12]/div/div/span[2]/button',
        'profit': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[5]/div['
                  '12]/div/div/span[1]/strong[2]/span[2]'
    },
    'USDCHF': {
        'sell': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[6]/div[4]/button',
        'buy': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[6]/div[6]/button',
        'close': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[6]/div['
                 '12]/div/div/span[2]/button',
        'profit': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[6]/div['
                  '12]/div/div/span[1]/strong[2]/span[2]'
    },
    'EURJPY': {
        'sell': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[7]/div[4]/button',
        'buy': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[7]/div[6]/button',
        'close': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[7]/div['
                 '12]/div/div/span[2]/button',
        'profit': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[7]/div['
                  '12]/div/div/span[1]/strong[2]/span[2]'
    },
    'EURGPB': {
        'sell': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[8]/div[4]/button',
        'buy': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[8]/div[6]/button',
        'close': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[8]/div['
                 '12]/div/div/span[2]/button',
        'profit': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[8]/div['
                  '12]/div/div/span[1]/strong[2]/span[2]'
    },
    'GBPJPY': {
        'sell': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[9]/div[4]/button',
        'buy': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[9]/div[6]/button',
        'close': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[9]/div['
                 '12]/div/div/span[2]/button',
        'profit': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[9]/div['
                  '12]/div/div/span[1]/strong[2]/span[2]'
    },
    'EURAUD': {
        'sell': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[10]/div[4]/button',
        'buy': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[10]/div[6]/button',
        'close': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[10]/div['
                 '12]/div/div/span[2]/button',
        'profit': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[10]/div['
                  '12]/div/div/span[1]/strong[2]/span[2]'
    },
    'EURNZD': {
        'sell': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[11]/div[4]/button',
        'buy': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[11]/div[6]/button',
        'close': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[11]/div['
                 '12]/div/div/span[2]/button',
        'profit': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[11]/div['
                  '12]/div/div/span[1]/strong[2]/span[2]'
    },
    'EURCAD': {
        'sell': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[12]/div[4]/button',
        'buy': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[12]/div[6]/button',
        'close': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[12]/div['
                 '12]/div/div/span[2]/button',
        'profit': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[9]/div['
                  '12]/div/div/span[1]/strong[2]/span[2]'
    },
    'EURCHF': {
        'sell': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[13]/div[4]/button',
        'buy': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[13]/div[6]/button',
        'close': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[13]/div['
                 '12]/div/div/span[2]/button',
        'profit': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[13]/div['
                  '12]/div/div/span[1]/strong[2]/span[2]'
    },
    'NZDUSD': {
        'sell': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[14]/div[4]/button',
        'buy': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[14]/div[6]/button',
        'close': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[14]/div['
                 '12]/div/div/span[2]/button',
        'profit': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[14]/div['
                  '12]/div/div/span[1]/strong[2]/span[2]'
    },
    'AUDCAD': {
        'sell': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[15]/div[4]/button',
        'buy': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[15]/div[6]/button',
        'close': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[15]/div['
                 '12]/div/div/span[2]/button',
        'profit': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[15]/div['
                  '12]/div/div/span[1]/strong[2]/span[2]'
    },
    'AUDCHF': {
        'sell': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[16]/div[4]/button',
        'buy': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[16]/div[6]/button',
        'close': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[16]/div['
                 '12]/div/div/span[2]/button',
        'profit': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[16]/div['
                  '12]/div/div/span[1]/strong[2]/span[2]'
    },
    'AUDJPY': {
        'sell': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[17]/div[4]/button',
        'buy': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[17]/div[6]/button',
        'close': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[17]/div['
                 '12]/div/div/span[2]/button',
        'profit': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[17]/div['
                  '12]/div/div/span[1]/strong[2]/span[2]'
    },
    'AUDNZD': {
        'sell': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[18]/div[4]/button',
        'buy': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[18]/div[6]/button',
        'close': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[18]/div['
                 '12]/div/div/span[2]/button',
        'profit': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[18]/div['
                  '12]/div/div/span[1]/strong[2]/span[2]'
    },
    'CADCHF': {
        'sell': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[19]/div[4]/button',
        'buy': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[19]/div[6]/button',
        'close': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[19]/div['
                 '12]/div/div/span[2]/button',
        'profit': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[19]/div['
                  '12]/div/div/span[1]/strong[2]/span[2]'
    },
    'CADJPY': {
        'sell': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[20]/div[4]/button',
        'buy': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[20]/div[6]/button',
        'close': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[20]/div['
                 '12]/div/div/span[2]/button',
        'profit': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[20]/div['
                  '12]/div/div/span[1]/strong[2]/span[2]'
    },
    'CHFJPY': {
        'sell': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[21]/div[4]/button',
        'buy': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[21]/div[6]/button',
        'close': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[21]/div['
                 '12]/div/div/span[2]/button',
        'profit': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[21]/div['
                  '12]/div/div/span[1]/strong[2]/span[2]'
    },
    'GBPAUD': {
        'sell': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[22]/div[4]/button',
        'buy': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[22]/div[6]/button',
        'close': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[22]/div['
                 '12]/div/div/span[2]/button',
        'profit': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[22]/div['
                  '12]/div/div/span[1]/strong[2]/span[2]'
    },
    'GBPCAD': {
        'sell': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[23]/div[4]/button',
        'buy': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[23]/div[6]/button',
        'close': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[23]/div['
                 '12]/div/div/span[2]/button',
        'profit': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[23]/div['
                  '12]/div/div/span[1]/strong[2]/span[2]'
    },
    'GBPCHF': {
        'sell': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[24]/div[4]/button',
        'buy': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[24]/div[6]/button',
        'close': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[24]/div['
                 '12]/div/div/span[2]/button',
        'profit': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[24]/div['
                  '12]/div/div/span[1]/strong[2]/span[2]'
    },
    'GBPNZD': {
        'sell': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[25]/div[4]/button',
        'buy': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[25]/div[6]/button',
        'close': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[25]/div['
                 '12]/div/div/span[2]/button',
        'profit': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[25]/div['
                  '12]/div/div/span[1]/strong[2]/span[2]'
    },
    'NZDCAD': {
        'sell': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[26]/div[4]/button',
        'buy': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[26]/div[6]/button',
        'close': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[26]/div['
                 '12]/div/div/span[2]/button',
        'profit': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[26]/div['
                  '12]/div/div/span[1]/strong[2]/span[2]'
    },
    'NZDCHF': {
        'sell': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[27]/div[4]/button',
        'buy': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[27]/div[6]/button',
        'close': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[27]/div['
                 '12]/div/div/span[2]/button',
        'profit': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[27]/div['
                  '12]/div/div/span[1]/strong[2]/span[2]'
    },
    'NZDJPY': {
        'sell': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[28]/div[4]/button',
        'buy': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[28]/div[6]/button',
        'close': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[28]/div['
                 '12]/div/div/span[2]/button',
        'profit': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[28]/div['
                  '12]/div/div/span[1]/strong[2]/span[2]'
    },
    'USDSGD': {
        'sell': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[29]/div[4]/button',
        'buy': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[29]/div[6]/button',
        'close': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[29]/div['
                 '12]/div/div/span[2]/button',
        'profit': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[29]/div['
                  '12]/div/div/span[1]/strong[2]/span[2]'
    },
    'AUDSGD': {
        'sell': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[30]/div[4]/button',
        'buy': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[30]/div[6]/button',
        'close': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[30]/div['
                 '12]/div/div/span[2]/button',
        'profit': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[30]/div['
                  '12]/div/div/span[1]/strong[2]/span[2]'
    },
    'EURSGD': {
        'sell': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[31]/div[4]/button',
        'buy': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[31]/div[6]/button',
        'close': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[31]/div['
                 '12]/div/div/span[2]/button',
        'profit': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[31]/div['
                  '12]/div/div/span[1]/strong[2]/span[2]'
    },
    'GBPSGD': {
        'sell': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[32]/div[4]/button',
        'buy': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[32]/div[6]/button',
        'close': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[32]/div['
                 '12]/div/div/span[2]/button',
        'profit': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[32]/div['
                  '12]/div/div/span[1]/strong[2]/span[2]'
    },
    'CHFDKK': {
        'sell': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[33]/div[4]/button',
        'buy': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[33]/div[6]/button',
        'close': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[33]/div['
                 '12]/div/div/span[2]/button',
        'profit': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[33]/div['
                  '12]/div/div/span[1]/strong[2]/span[2]'
    },
    'CHFNOK': {
        'sell': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[34]/div[4]/button',
        'buy': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[34]/div[6]/button',
        'close': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[34]/div['
                 '12]/div/div/span[2]/button',
        'profit': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[34]/div['
                  '12]/div/div/span[1]/strong[2]/span[2]'
    },
    'CHFSEK': {
        'sell': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[35]/div[4]/button',
        'buy': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[35]/div[6]/button',
        'close': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[35]/div['
                 '12]/div/div/span[2]/button',
        'profit': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[35]/div['
                  '12]/div/div/span[1]/strong[2]/span[2]'
    },
    'EURDKK': {
        'sell': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[36]/div[4]/button',
        'buy': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[36]/div[6]/button',
        'close': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[36]/div['
                 '12]/div/div/span[2]/button',
        'profit': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[36]/div['
                  '12]/div/div/span[1]/strong[2]/span[2]'
    },
    'EURMXN': {
        'sell': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[37]/div[4]/button',
        'buy': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[37]/div[6]/button',
        'close': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[37]/div['
                 '12]/div/div/span[2]/button',
        'profit': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[37]/div['
                  '12]/div/div/span[1]/strong[2]/span[2]'
    },
    'EURNOK': {
        'sell': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[38]/div[4]/button',
        'buy': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[38]/div[6]/button',
        'close': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[38]/div['
                 '12]/div/div/span[2]/button',
        'profit': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[38]/div['
                  '12]/div/div/span[1]/strong[2]/span[2]'
    },
    'EURPLN': {
        'sell': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[39]/div[4]/button',
        'buy': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[39]/div[6]/button',
        'close': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[39]/div['
                 '12]/div/div/span[2]/button',
        'profit': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[39]/div['
                  '12]/div/div/span[1]/strong[2]/span[2]'
    },
    'EURSEK': {
        'sell': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[40]/div[4]/button',
        'buy': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[40]/div[6]/button',
        'close': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[40]/div['
                 '12]/div/div/span[2]/button',
        'profit': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[40]/div['
                  '12]/div/div/span[1]/strong[2]/span[2]'
    },
    'EURZAR': {
        'sell': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[41]/div[4]/button',
        'buy': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[41]/div[6]/button',
        'close': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[41]/div['
                 '12]/div/div/span[2]/button',
        'profit': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[41]/div['
                  '12]/div/div/span[1]/strong[2]/span[2]'
    },
    'GBPDKK': {
        'sell': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[42]/div[4]/button',
        'buy': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[42]/div[6]/button',
        'close': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[42]/div['
                 '12]/div/div/span[2]/button',
        'profit': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[42]/div['
                  '12]/div/div/span[1]/strong[2]/span[2]'
    },
    'GBPNOK': {
        'sell': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[43]/div[4]/button',
        'buy': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[43]/div[6]/button',
        'close': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[43]/div['
                 '12]/div/div/span[2]/button',
        'profit': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[43]/div['
                  '12]/div/div/span[1]/strong[2]/span[2]'
    },
    'GBPSEK': {
        'sell': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[44]/div[4]/button',
        'buy': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[44]/div[6]/button',
        'close': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[44]/div['
                 '12]/div/div/span[2]/button',
        'profit': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[44]/div['
                  '12]/div/div/span[1]/strong[2]/span[2]'
    },
    'GBPZAR': {
        'sell': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[45]/div[4]/button',
        'buy': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[45]/div[6]/button',
        'close': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[45]/div['
                 '12]/div/div/span[2]/button',
        'profit': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[45]/div['
                  '12]/div/div/span[1]/strong[2]/span[2]'
    },
    'USDZNH': {
        'sell': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[46]/div[4]/button',
        'buy': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[46]/div[6]/button',
        'close': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[46]/div['
                 '12]/div/div/span[2]/button',
        'profit': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[46]/div['
                  '12]/div/div/span[1]/strong[2]/span[2]'
    },
    'USDDKK': {
        'sell': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[47]/div[4]/button',
        'buy': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[47]/div[6]/button',
        'close': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[47]/div['
                 '12]/div/div/span[2]/button',
        'profit': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[47]/div['
                  '12]/div/div/span[1]/strong[2]/span[2]'
    },
    'USDHKD': {
        'sell': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[48]/div[4]/button',
        'buy': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[48]/div[6]/button',
        'close': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[48]/div['
                 '12]/div/div/span[2]/button',
        'profit': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[48]/div['
                  '12]/div/div/span[1]/strong[2]/span[2]'
    },
    'USDMXN': {
        'sell': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[49]/div[4]/button',
        'buy': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[49]/div[6]/button',
        'close': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[49]/div['
                 '12]/div/div/span[2]/button',
        'profit': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[49]/div['
                  '12]/div/div/span[1]/strong[2]/span[2]'
    },
    'USDNOK': {
        'sell': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[50]/div[4]/button',
        'buy': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[50]/div[6]/button',
        'close': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[50]/div['
                 '12]/div/div/span[2]/button',
        'profit': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[50]/div['
                  '12]/div/div/span[1]/strong[2]/span[2]'
    },
    'USDPLN': {
        'sell': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[51]/div[4]/button',
        'buy': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[51]/div[6]/button',
        'close': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[51]/div['
                 '12]/div/div/span[2]/button',
        'profit': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[51]/div['
                  '12]/div/div/span[1]/strong[2]/span[2]'
    },
    'USDSEK': {
        'sell': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[52]/div[4]/button',
        'buy': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[52]/div[6]/button',
        'close': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[52]/div['
                 '12]/div/div/span[2]/button',
        'profit': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[52]/div['
                  '12]/div/div/span[1]/strong[2]/span[2]'
    },
    'USDZAR': {
        'sell': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[53]/div[4]/button',
        'buy': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[53]/div[6]/button',
        'close': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[53]/div['
                 '12]/div/div/span[2]/button',
        'profit': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[53]/div['
                  '12]/div/div/span[1]/strong[2]/span[2]'
    },
    'SGDJPY': {
        'sell': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[54]/div[4]/button',
        'buy': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[54]/div[6]/button',
        'close': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[54]/div['
                 '12]/div/div/span[2]/button',
        'profit': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[54]/div['
                  '12]/div/div/span[1]/strong[2]/span[2]'
    },
    'DKKNOK': {
        'sell': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[55]/div[4]/button',
        'buy': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[55]/div[6]/button',
        'close': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[55]/div['
                 '12]/div/div/span[2]/button',
        'profit': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[55]/div['
                  '12]/div/div/span[1]/strong[2]/span[2]'
    },
    'SEKNOK': {
        'sell': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[56]/div[4]/button',
        'buy': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[56]/div[6]/button',
        'close': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[56]/div['
                 '12]/div/div/span[2]/button',
        'profit': '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[2]/div[56]/div['
                  '12]/div/div/span[1]/strong[2]/span[2]'
    }
}

# this json contains xpaths to all buttons when configuring a position
position_configure_elements = {
    'input': '/html/body/div[1]/div[2]/div/div/div/div[2]/div/div[1]/div[3]/div[1]/div/div[2]/input',
    'plus': '/html/body/div[1]/div[2]/div/div/div/div[2]/div/div[1]/div[3]/div[1]/div/div[2]/button[1]',
    'minus': '/html/body/div[1]/div[2]/div/div/div/div[2]/div/div[1]/div[3]/div[1]/div/div[2]/button[2]',
    'amount': '/html/body/div[1]/div[2]/div/div/div/div[2]/div/div[1]/div[3]/div[1]/div/div[3]/p/strong',
    'finish': '/html/body/div[1]/div[2]/div/div/div/div[2]/div/div[1]/div[3]/div[3]/div[1]/button'
}

# setup
# initialize the chrome driver and open the plus500 website,
# I give the driver access to my user data so that it will log into plus500 automatically
options = webdriver.ChromeOptions()
options.add_argument(r"user-data-dir=C:\Users\idans\AppData\Local\Google\Chrome\User Data")
capabilities = DesiredCapabilities.CHROME
capabilities["loggingPrefs"] = {"performance": "ALL"}
capabilities["goog:loggingPrefs"] = {"performance": "ALL"}
driver = webdriver.Chrome(executable_path='C:\Program Files\ChromeDriver\chromedriver.exe', options=options,
                          desired_capabilities=capabilities)
driver.get("https://app.plus500.com/trade/major")

driver.set_page_load_timeout(30)

time.sleep(5)

# navigate to the 'my favorites' tab
driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[1]/div/ul[4]/li['
                              '1]/ul/li[3]').click()

time.sleep(1)

# read off the website how much money I have
def get_available_money():
    return float(driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/header/div/div[3]/span[1]/ul/li[1]/span')
                 .text
                 .replace('₪', '')
                 .replace('\u202a', '')
                 .replace('\u202c', '')
                 .replace(',', ''))


# open a position on a specified chart with a specified open price
def open_position(type='', chart_name='', open_price=100):
    try:
        if not (type == 's' or type == 'b'):
            print('order attempt error: please provide a valid order type')
            return False

        try:
            driver.find_element(By.XPATH, '/html/body/div[2]/div[3]/div[2]/button[2]').click()
        except:
            pass

        time.sleep(3)

        if type == 's':
            driver.find_element(By.XPATH, chart_buttons_xpaths[chart_name]['sell']).click()
        elif type == 'b':
            driver.find_element(By.XPATH, chart_buttons_xpaths[chart_name]['buy']).click()

        time.sleep(0.5)

        input_field = driver.find_element(By.XPATH, position_configure_elements['input'])
        input_field.send_keys(Keys.CONTROL + "a")
        input_field.send_keys(Keys.DELETE)
        time.sleep(0.5)
        input_field.send_keys('0')

        minus = driver.find_element(By.XPATH, position_configure_elements['minus'])
        plus = driver.find_element(By.XPATH, position_configure_elements['plus'])

        minus.click()

        amount = driver.find_element(By.XPATH, position_configure_elements['amount'])

        time.sleep(1)

        # configure the position by interacting with the UI, raising the price until it's above the requested open_price
        while True:
            if float(amount.text.split('= ₪')[1].replace('\u202a', '').replace('\u202c', '').replace(',',
                                                                                                     '')) > open_price:
                driver.find_element(By.XPATH, position_configure_elements['finish']).click()
                return True

            plus.click()

            time.sleep(1)

    except Exception as e:
        return False


# close a position on a specified chart
def close_position(chart_name):
    try:
        try:
            driver.find_element(By.XPATH, '/html/body/div[2]/div[3]/div[2]/button[2]').click()
        except:
            pass

        time.sleep(3)

        driver.find_element(By.XPATH, chart_buttons_xpaths[chart_name]['close']).click()

        time.sleep(2)

        driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div/div/div/div[2]/div/div/div/div[3]/div[3]/div['
                                      '1]/button').click()

        try:
            return str(driver.find_element(By.XPATH, chart_buttons_xpaths[chart_name]['profit']).text)
        except:
            return 'could not get profit'
    except Exception as e:
        return 'ERROR'
