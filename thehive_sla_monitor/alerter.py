from thehive_sla_monitor.logger import logging

class Alerter():
    def __init__(self):
        self.hive_30_list = []
        hive_30_dict = {}

        self.hive_45_list = []
        hive_45_dict = {}

        self.hive_60_list = []
        hive_60_dict = {}

        ignore_list = []
        called_list = []


    def add_to_30m(self, id):
        if id in self.hive_30_list:
            logging.info('Already added - 30 minute SLA list: %s' % id)
        else:
            self.hive_30_list.append(id)


    def add_to_45m(self, id):
        if id in self.hive_45_list:
            logging.info('Already added - 45 minute SLA list: %s' % id)
        else:
            self.hive_45_list.append(id)


    def add_to_60m(self, id):
        if id in self.hive_60_list:
            logging.info('Already added - 60 minute SLA list: %s' % id)
        else:
            self.hive_60_list.append(id)