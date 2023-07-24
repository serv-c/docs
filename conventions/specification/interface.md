# Interfaces

## HTTP Interface

The following routes are reserved and should be implemented to respond to the following requests,

```
GET  /health      // respond 200 if okay, 500 if not
GET  /ready       // respond 200 if ready, 500 if not
POST /:prefix     // send a message with route prefix
POST /id/:id      // set an id parameter in cache
GET  /id/:id      // get value of id in cache.
                     a null value means it does not exist.
```
