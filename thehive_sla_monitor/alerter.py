from multiprocessing import Process, Manager

from thehive_sla_monitor.logger import logging

hive_30_dict = {}
hive_45_dict = {}
hive_60_dict = {}

hive_30_list = []
hive_45_list = []
hive_60_list = []

ignore_list = []
called_list = []

manager = Manager()
alert_dict = manager.dict()

class Alerter():
    def add_to_30m(self, id):
        if id in hive_30_list:
            logging.info('Already added - 30 minute SLA list: %s' % id)
        else:
            hive_30_list.append(id)

    def add_to_45m(self, id):
        if id in hive_45_list:
            logging.info('Already added - 45 minute SLA list: %s' % id)
        else:
            hive_45_list.append(id)

    def add_to_60m(self, id):
        if id in hive_60_list:
            logging.info('Already added - 60 minute SLA list: %s' % id)
        else:
            hive_60_list.append(id)


    def add_to_30_dict(self, id, rule_name):
        hive_30_dict.update({ id : rule_name })


    def add_to_45_dict(self, id, rule_name):
        hive_45_dict.update({ id : rule_name })
    

    def add_to_60_dict(self, id, rule_name):
        hive_60_dict.update({ id : rule_name })