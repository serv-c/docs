# Configuration

Environment variables can be used to set the values of the paramter. For example, to set `conn.DATABASE_URL`, the environment variable `CONN_DATABASE_URL` will be read as the default.

## Connection Configuration

- CONN_CACHE_URL - The connection url to the cache middleware
  - alias: CACHE_URL
- CONN_DATABASE_URL - The connection url to the database server
  - alias: DATABASE_URL
- CONN_BUS_URL - The connection url to the service bus
  - alias: BUS_URL

## Bus Configuration

- EVENTEXCHANGENAME - the exchange name to use for event. default: 'amqp.fanout'
- EXCHANGENAME - the exchange name to use for normal bus communication. default: ''
- PREFIX - the prefix to use for routing keys. default: ''

## Server Configuration

- PORT - the port for the web interface to listen onto. default: 3000
- INSTANCE_ID - the instance id to use to uniquely identify the server. default: hostname
