import threading

"""
This file is responsible for keeping an in-memory track of Hive alerts and there current associated SLA tier.
"""

hive_30_list = []
hive_30_dict = {}

hive_45_list = []
hive_45_dict = {}

hive_60_list = []
hive_60_dict = {}

ignore_list = []
called_list = []

def add_to_30m(id):
  if id in hive_30_list:
    logging.info('Already added - 30 minute SLA list: ' + id)
  else:
    logging.info('Appending - 30 minute SLA list: ' + id)
    hive_30_list.append(id)

def add_to_45m(id):
  if id in hive_45_list:
    logging.info('Already added - 45 minute SLA list: ' + id)
  else:
    logging.info('Appending - 45 minute SLA list: ' + id)
    hive_45_list.append(id)

def add_to_60m(id):
  if id in hive_60_list:
    logging.info('Already added - 60 minute SLA list: ' + id)
  else:
    logging.info('Appending - 60 minute SLA list: ' + id)
    hive_60_list.append(id)


def clean_ignore_list(id):
  t.sleep(3600)
  logging.info("Removing " + id + " from ignore list")
  ignore_list.remove(id)

def add_to_temp_ignore(id):
  logging.info("Adding " + id + " to ignore list")
  ignore_list.append(id)
  ignore_thread = threading.Thread(target=clean_ignore_list)
  ignore_thread.start()
  return id

def add_to_called_list(id):
  logging.info("Adding " + id + " to called list")
  called_list.append(id)
  return id

def is_empty(any_structure):
    if any_structure:
        return False
    else:
        return True
