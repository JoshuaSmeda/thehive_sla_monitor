import configuration

print(configuration.SLA_SETTINGS)

if configuration.SLA_SETTINGS['SEVERITY_1']['ENABLED'] == True:
  print("YEA")
  print("timer for low is set to %s" % configuration.SLA_SETTINGS['SEVERITY_1']['LOW_SEVERITY']['TIMER'])
