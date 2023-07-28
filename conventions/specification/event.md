# Event

Events are emitted via the bus on the `eventExchangeName`. Not all services need to process every event. Servers that are type 'EventEmitters' will only emit events and not respond to messages.

## Process Diagram

```mermaid
sequenceDiagram
  actor Client1
  actor Client2
  actor Client3
  participant Topic1
  participant Topic2
  box Middleware
    participant Bus
  end
  participant Service

  Client1--)Topic1: Subscribe
  Client2--)Topic2: Subscribe
  Client3--)Topic2: Subscribe

  Service-)Bus: Emits event to EventExchange
  par
    Bus-)Topic1: Receives event
    Topic1-)Client1: Deliver Event
  and
    Bus-)Topic2: Receives event
    Note over Client2,Client3: One Client per Topic
    Topic2-)Client3: Deliver Event
  end
```

## Structure

```javascript
{
  "type": "event"
  "route": "string"         // routing key to the event Emitter
  "instanceId": "string"    // instance id of event Emitter
  "event":  "string"        // event name
  "details": "string|json"  // details attributed to event
}
```
