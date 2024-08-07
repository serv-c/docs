# Configuration

The configurations are all specified here. Configurations can be set through yaml configuration file using the path configured by environment variable `CONF__FILE` which will default to `/config/config.yaml`. When being set via environment variable, the `__` will represent when going down in a section and should be all uppercase. For example, `conf.bus.url` can be set via the environment variable `CONF__BUS__URL`.

```yaml
conf:
  # the location of the configuration file. Obviously can only be set via environment variables.
  file: /config/config.yaml
  instanceId: str   # defaults to hostname

  # configuration for the bus
  bus:
    url: str # connection string
    prefix: str # prefix to use when subscribing to a route
    route: str # name used when subscribing

    # prefix to use when sending a message. must be used exclusive
    # to each other. sendPrefix will submit the message with a prefix for all routes. routePrefix allows you to submit a prefix for specific routes only.
    sendPrefix: str
    routePrefix: {} # <route>: prefix. if set via environment variable, will be expecting a string to be loaded via a json parser
    
    # when about to send a 400 or 500, exit the program instead of responding with an error response. This is useful to force services to always exit cleanly in nonproduction environments.
    exitOn4XX: bool 
    exitOn500: bool

  cache:
    url: str # connection string

  http:
    port: 3000
```
