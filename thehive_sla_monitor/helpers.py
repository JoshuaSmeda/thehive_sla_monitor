import threading

"""
This file is responsible for keeping an in-memory track of Hive alerts and there current associated SLA tier.
"""
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
