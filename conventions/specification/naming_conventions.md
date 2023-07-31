# Naming Conventions

TODO: update with new names

```
repository name: svc-[dns-compliant-name]
npm artifact name: servc-svc-[dns-compliant-name]
container artifact name: servcorg/svc-[dns-compliant-name]
topic/route: svc-[dns-compliant-name]
event route:
  svc.event.[dns-compliant-instance].[verb]
  svc.event.[dns-compliant-category].[verb]
```

example:

```
repository name: svc-deluge
npm artifact name: servc-svc-deluge
container artifact name: servcorg/svc-deluge
topic/route: svc-deluge
event route:
  svc.event.deluge.completed-task
  svc.event.dl.completed-task
```
