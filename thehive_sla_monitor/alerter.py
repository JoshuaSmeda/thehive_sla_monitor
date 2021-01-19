"""
This module handles all objects for storing alerts and their approriate SLA tiers
"""

from multiprocessing import Manager
from thehive_sla_monitor.logger import logging

# Define variables
low_sev_dict = {}
med_sev_dict = {}
high_sev_dict = {}

low_sev_list = ['1234']
med_sev_list = ['1234']
high_sev_list = ['1234']
ignore_list = []

# WIP
called_list = []
message_list = []
message_dict = {}
seen_list = []
slack_dict = {}

# Multiprocessing queue manager
manager = Manager()
alert_dict = manager.dict()


class Alerter():
    def add_to_low_sev(self, id):
        if id in low_sev_list:
            logging.info('Already added - LOW severity SLA list: %s' % id)
        else:
            low_sev_list.append(id)

    def add_to_med_sev(self, id):
        if id in med_sev_list:
            logging.info('Already added - MEDIUM severity SLA list: %s' % id)
        else:
            med_sev_list.append(id)

    def add_to_high_sev(self, id):
        if id in high_sev_list:
            logging.info('Already added - HIGH severity SLA list: %s' % id)
        else:
            high_sev_list.append(id)

    def add_to_low_sev_dict(self, id, rule_name):
        low_sev_dict.update({id: rule_name})

    def add_to_med_sev_dict(self, id, rule_name):
        med_sev_dict.update({id: rule_name})

    def add_to_high_sev_dict(self, id, rule_name):
        high_sev_dict.update({id: rule_name})
