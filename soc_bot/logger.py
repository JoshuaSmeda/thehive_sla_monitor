from datetime import datetime, timedelta, time, date
import dateutil.parser
import logging
import logging.handlers
import os

# Setup Syslog logging

def log_current_time():
  current_time = datetime.now()
  return current_time

log = logging.getLogger(__name__)
log.root.setLevel(logging.DEBUG)
log_formatter = logging.Formatter('%(levelname)s %(message)s')
log_handler = logging.StreamHandler()
log_handler.setFormatter(log_formatter)
log.addHandler(log_handler)

log_directory = '/opt/soc_bot/logs/'

if os.path.isdir(log_directory) == False:
  print("Creating Log Directory")
  os.mkdir(log_directory)
else:
  print("Log Directory Exists")

def get_log_date_log():
  date = datetime.now()
  dt_log = date.strftime("%Y-%m-%d %H:%M:%S")
  return dt_log

def get_log_date_file():
  date = datetime.now()
  dt_file = date.strftime("%Y-%m-%d")
  return dt_file

def write_file(file_name, data_to_write):
  try:
    with open(file_name, 'a') as f:
      f.write(data_to_write.encode('utf-8'))
      f.write("\n")
  except Exception as error:
    log.error('Error writing file ' + file_name + '. Cannot continue. Exception: ' + str(error))
    quit()

def collect_logs(response):
  current_dt = get_log_date_file()
  global file_name
  file_name = current_dt + '.log'
  write_file(os.path.join(log_directory, file_name), response)
