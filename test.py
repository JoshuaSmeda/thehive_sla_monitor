import configuration

config = configuration.SLA_SETTINGS


for x in config:
    for e in config[x]:
      if e == 'ENABLED':
        for f in config[x]:
          if f == 'ENABLED':
            continue
          for z in config[x][f]:
            print(config[x][f][z])
