
config = {
'THEHIVE_LEVEL1': {'ENABLED'        : True,
                   'LOW_SEVERITY'   : {'TIMER': 1800, 'NOTIFICATION_METHOD': ['SLACK', 'TWILIO_SMS']},
                   'MEDIUM_SEVERITY': {'TIMER': 2700, 'NOTIFICATION_METHOD': ['SLACK', 'TWILIO_ESC']}},

'THEHIVE_LEVEL2': {'ENABLED': False,
                   'MEDIUM_SEVERITY': {'TIMER': 2700, 'NOTIFICATION_METHOD': ['SLACK', 'TWILIO_SMS']}}
#                     'HIGH_SEVERITY'  : {'TIMER': 3600, 'NOTIFICATION_METHOD': ['SLACK', 'TWILIO_CALL']}},

}


def get_active_dict(dct):
  active_dicts = []
  for obj in dct:
    if dct[obj]['ENABLED']:
      active_dicts.append(obj)

  return active_dicts


def get_nested_dict(dct, obj):
  d1 = {}
  keys = []
  for element in dct[obj]:
    if 'ENABLED' in element:
      continue # Skip enabled obj
    keys.append(element)
  for k in keys:
    d1[k] = {'TIMER': dct[obj][k]['TIMER'], 'NOTIFICATION_METHOD': dct[obj][k]['NOTIFICATION_METHOD']}

  t = ()
  for d in d1:
    t += (d1[d],)
  print(t)
  return t
 

a = get_active_dict(config)

for value in a:
  print("Returning configuration for %s" % value)
  l, m = get_nested_dict(config, value)
  print(l)
  print(m)
