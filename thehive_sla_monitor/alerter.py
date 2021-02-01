"""
This module handles all objects for storing alerts and their approriate SLA tiers
"""

from multiprocessing import Manager
from thehive_sla_monitor.logger import logging

# Define variables
low_sev_list = []
med_sev_list = []
high_sev_list = []
ignore_list = []
called_list = []
seen_list = []
message_list = []
alerter_dict = {}

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

    def add_to_alerter_dict(self, id, rule_name):
        alerter_dict.update({id: rule_name})
