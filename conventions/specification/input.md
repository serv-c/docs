# Input Payload Structure

```javascript
{
  "id": "string"
  "route": "string"
  "argumentId": "string"  // should be prefixed with arg_

  "instanceId"?: "string"
  "conn"?: <CONN>
  "log"?: <LOG>
  "busConf"?: <BUSCONF>
}

CONN = PARTIAL<{
  "CACHE_URL": "string"
  "DATABASE_URL": "string"
  "BUS_URL": "string"
}>

LOG = PARTIAL<{
  "type": "http|bus|database"  // default database
  "metrics": [
    "serviceName",
    "instanceId",
    "inputPayload",
    "duration",
    "statusCode",
    "isError"
  ]
  "database": PARTIAL<{
    "tableName": "logging",
    "columnMap": PARTIAL<{
      [metricName]: "database columnName"
    }>
  }>
}>

BUSCONF = PARTIAL<{
  eventExchangeName: "string"   // default: amq.fanout
  exchangeName: "string"        // default: direct
  routePrefix: "string"              // default: ""
}>
```

## Startup Arguments

The program should accept all optional arguments as a JSON encoded string as the first argument.
