# Resolvers

All services handle events and inputs using resolvers. The only two types of input are an event or an input.

## Input Resolvers

Descrimination between input resolvers is identified by matching the method in the argument artifiact. The resolver that matches by name to the `method` parameter will be utilized to resolve the input and provide a response.

| Arugment  | Type             | Description                                                                                                                                   |
| --------- | ---------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| id        | string           | the id of the input message                                                                                                                   |
| bus       | Bus              | the bus class that recieved the message                                                                                                       |
| cache     | Cache            | the cache class that contains the argument artifact. this should be used to store the response artifact.                                      |
| inputs    | ArgumentArtifact | the argumentartifact with all the inputs retrieved from the cache                                                                             |
| emitEvent | function         | A function that can be used to emit events into the bus. It accepts to arguments, eventName:string and the details as an serializable object. |

## Event Resolvers

Descrimination between event resolvers is identified by matching the `event` in the event payload. The resolver that matches by name to the `event` parameter will be utilized to resolve the event and do any required processing.

| Arugment   | Type     | Description                                                                                                                                   |
| ---------- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| bus        | Bus      | the bus class that recieved the message                                                                                                       |
| cache      | Cache    | the cache class that contains the argument artifact. this should be used to store the response artifact.                                      |
| route      | string   | the route of the event emitter                                                                                                                |
| instanceId | string   | the instanceId of the event emitter                                                                                                           |
| details    | Object   | the details attributed to the event                                                                                                           |
| emitEvent  | function | A function that can be used to emit events into the bus. It accepts to arguments, eventName:string and the details as an serializable object. |
